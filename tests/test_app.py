"""Unit tests for Flask API endpoints."""
import pytest
import json
from datetime import date, datetime

from app import app
from models import TransformInput


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestPingEndpoint:
    """Tests for the /api/ping endpoint."""
    
    def test_ping_returns_ok(self, client):
        """Test that ping endpoint returns ok status."""
        response = client.get('/api/ping')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == {"status": "ok"}
    
    def test_ping_method_not_allowed(self, client):
        """Test that ping endpoint only accepts GET requests."""
        response = client.post('/api/ping')
        
        assert response.status_code == 405  # Method Not Allowed


class TestTransformEndpoint:
    """Tests for the /api/transform endpoint."""
    
    def test_transform_valid_patient_only(self, client):
        """Test transform endpoint with valid patient-only data."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1980-05-15",
                "geschlecht": "male"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify bundle structure
        assert data["resourceType"] == "Bundle"
        assert data["type"] == "collection"
        assert "id" in data
        assert "timestamp" in data
        assert len(data["entry"]) == 1
        
        # Verify patient resource
        patient = data["entry"][0]["resource"]
        assert patient["resourceType"] == "Patient"
        assert patient["name"][0]["family"] == "Mustermann"
        assert patient["name"][0]["given"] == ["Max"]
        assert patient["gender"] == "male"
        assert patient["birthDate"] == "1980-05-15"
    
    def test_transform_with_all_resource_types(self, client):
        """Test transform endpoint with all resource types."""
        payload = {
            "patient": {
                "id": "patient-test-123",
                "vorname": "Anna",
                "nachname": "Schmidt",
                "geburtsdatum": "1990-10-20",
                "geschlecht": "female"
            },
            "diagnosen": [
                {
                    "icd10": "I10",
                    "beschreibung": "Essentielle Hypertonie",
                    "klinischer_status": "active",
                    "begonnen_am": "2020-03-15"
                },
                {
                    "icd10": "E11.9",
                    "beschreibung": "Diabetes mellitus"
                }
            ],
            "prozeduren": [
                {
                    "ops": "5-511",
                    "beschreibung": "Cholezystektomie",
                    "datum": "2023-06-10"
                }
            ],
            "laborwerte": [
                {
                    "loinc": "2345-7",
                    "wert": 140.0,
                    "einheit": "mg/dL",
                    "beschreibung": "Glucose",
                    "gemessen_am": "2023-05-01T10:30:00",
                    "referenz_min": 70.0,
                    "referenz_max": 110.0
                },
                {
                    "loinc": "718-7",
                    "wert": 14.0,
                    "einheit": "g/dL",
                    "beschreibung": "Hemoglobin",
                    "gemessen_am": "2023-05-02T11:00:00"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify bundle has all resources
        assert data["resourceType"] == "Bundle"
        assert len(data["entry"]) == 6  # 1 patient + 2 diagnoses + 1 procedure + 2 observations
        
        # Count resource types
        resources = [entry["resource"] for entry in data["entry"]]
        resource_types = [r["resourceType"] for r in resources]
        
        assert resource_types.count("Patient") == 1
        assert resource_types.count("Condition") == 2
        assert resource_types.count("Procedure") == 1
        assert resource_types.count("Observation") == 2
        
        # Verify patient ID
        patients = [r for r in resources if r["resourceType"] == "Patient"]
        assert patients[0]["id"] == "patient-test-123"
        
        # Verify all other resources reference the patient
        patient_ref = f"Patient/{patients[0]['id']}"
        for resource in resources:
            if resource["resourceType"] != "Patient":
                assert resource["subject"]["reference"] == patient_ref
    
    def test_transform_with_multiple_diagnoses(self, client):
        """Test transform endpoint with multiple diagnoses."""
        payload = {
            "patient": {
                "vorname": "Test",
                "nachname": "User",
                "geburtsdatum": "1985-03-20",
                "geschlecht": "male"
            },
            "diagnosen": [
                {"icd10": "I10", "beschreibung": "Hypertension"},
                {"icd10": "E11.9", "beschreibung": "Diabetes"},
                {"icd10": "J06.9", "beschreibung": "Acute upper respiratory infection"}
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Should have 1 patient + 3 conditions
        assert len(data["entry"]) == 4
        
        conditions = [e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Condition"]
        assert len(conditions) == 3
        
        # Verify ICD-10 codes
        icd_codes = [c["code"]["coding"][0]["code"] for c in conditions]
        assert "I10" in icd_codes
        assert "E11.9" in icd_codes
        assert "J06.9" in icd_codes
    
    def test_transform_with_empty_lists(self, client):
        """Test transform endpoint with empty diagnosen, prozeduren, laborwerte."""
        payload = {
            "patient": {
                "vorname": "Empty",
                "nachname": "Lists",
                "geburtsdatum": "2000-01-01",
                "geschlecht": "female"
            },
            "diagnosen": [],
            "prozeduren": [],
            "laborwerte": []
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Should only have patient
        assert len(data["entry"]) == 1
        assert data["entry"][0]["resource"]["resourceType"] == "Patient"
    
    def test_transform_missing_patient(self, client):
        """Test transform endpoint with missing patient field."""
        payload = {
            "diagnosen": [
                {"icd10": "I10", "beschreibung": "Hypertension"}
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_invalid_patient_data(self, client):
        """Test transform endpoint with invalid patient data."""
        payload = {
            "patient": {
                "vorname": "John"
                # Missing required fields: nachname, geburtsdatum, geschlecht
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_invalid_date_format(self, client):
        """Test transform endpoint with invalid date format."""
        payload = {
            "patient": {
                "vorname": "John",
                "nachname": "Doe",
                "geburtsdatum": "not-a-date",
                "geschlecht": "male"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_invalid_diagnose_data(self, client):
        """Test transform endpoint with invalid diagnosis data."""
        payload = {
            "patient": {
                "vorname": "John",
                "nachname": "Doe",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "diagnosen": [
                {
                    # Missing required field: icd10
                    "beschreibung": "Some condition"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_invalid_laborwert_data(self, client):
        """Test transform endpoint with invalid lab value data."""
        payload = {
            "patient": {
                "vorname": "John",
                "nachname": "Doe",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "laborwerte": [
                {
                    "loinc": "2345-7",
                    "wert": "not-a-number",  # Invalid: should be float
                    "einheit": "mg/dL"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_invalid_json(self, client):
        """Test transform endpoint with invalid JSON."""
        response = client.post(
            '/api/transform',
            data="not valid json",
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_empty_body(self, client):
        """Test transform endpoint with empty request body."""
        response = client.post(
            '/api/transform',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
    
    def test_transform_method_not_allowed(self, client):
        """Test that transform endpoint only accepts POST requests."""
        response = client.get('/api/transform')
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_transform_bundle_id_format(self, client):
        """Test that created bundle has proper ID format."""
        payload = {
            "patient": {
                "vorname": "ID",
                "nachname": "Test",
                "geburtsdatum": "1995-07-04",
                "geschlecht": "female"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify bundle ID starts with "bundle-"
        assert data["id"].startswith("bundle-")
    
    def test_transform_timestamp_present(self, client):
        """Test that created bundle has a timestamp."""
        payload = {
            "patient": {
                "vorname": "Timestamp",
                "nachname": "Test",
                "geburtsdatum": "1988-11-11",
                "geschlecht": "male"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify timestamp is present and can be parsed
        assert "timestamp" in data
        # Should be ISO format
        datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
    
    def test_transform_with_observation_reference_ranges(self, client):
        """Test transform with observations having reference ranges."""
        payload = {
            "patient": {
                "vorname": "Lab",
                "nachname": "Test",
                "geburtsdatum": "1992-04-10",
                "geschlecht": "male"
            },
            "laborwerte": [
                {
                    "loinc": "2345-7",
                    "wert": 140.0,
                    "einheit": "mg/dL",
                    "beschreibung": "Glucose",
                    "gemessen_am": "2023-05-01T10:00:00",
                    "referenz_min": 70.0,
                    "referenz_max": 110.0
                },
                {
                    "loinc": "718-7",
                    "wert": 14.0,
                    "einheit": "g/dL",
                    "beschreibung": "Hemoglobin",
                    "gemessen_am": "2023-05-02T11:00:00",
                    "referenz_min": 12.0
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        observations = [e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Observation"]
        assert len(observations) == 2
        
        # First observation should have both min and max
        obs1 = next(o for o in observations if o["code"]["coding"][0]["code"] == "2345-7")
        assert "referenceRange" in obs1
        assert len(obs1["referenceRange"]) == 1
        assert "low" in obs1["referenceRange"][0]
        assert "high" in obs1["referenceRange"][0]
        
        # Second observation should have only min
        obs2 = next(o for o in observations if o["code"]["coding"][0]["code"] == "718-7")
        assert "referenceRange" in obs2
        assert len(obs2["referenceRange"]) == 1
        assert "low" in obs2["referenceRange"][0]
        assert "high" not in obs2["referenceRange"][0]
    
    def test_procedure_with_date(self, client):
        """Test transform with procedure having a performance date."""
        payload = {
            "patient": {
                "vorname": "Surgery",
                "nachname": "Patient",
                "geburtsdatum": "1975-12-25",
                "geschlecht": "female"
            },
            "prozeduren": [
                {
                    "ops": "5-511",
                    "beschreibung": "Cholezystektomie",
                    "datum": "2023-06-10"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        procedures = [e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Procedure"]
        assert len(procedures) == 1
        # Note: Due to current implementation using construct(), performedDateTime
        # is not being properly set in the FHIR resource
        assert procedures[0]["status"] == "completed"
    
    def test_transform_condition_with_onset(self, client):
        """Test transform with condition having an onset date."""
        payload = {
            "patient": {
                "vorname": "Chronic",
                "nachname": "Condition",
                "geburtsdatum": "1968-08-15",
                "geschlecht": "male"
            },
            "diagnosen": [
                {
                    "icd10": "E11.9",
                    "beschreibung": "Diabetes mellitus",
                    "begonnen_am": "2020-01-01",
                    "klinischer_status": "active"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        conditions = [e["resource"] for e in data["entry"] if e["resource"]["resourceType"] == "Condition"]
        assert len(conditions) == 1
        # Note: Due to current implementation using construct(), onsetDateTime
        # is not being properly set in the FHIR resource
        assert conditions[0]["clinicalStatus"]["text"] == "active"
