"""
Integration tests for Flask API endpoints with error handling.
"""
import pytest
import json
from datetime import date

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestPingEndpoint:
    """Test the ping endpoint."""
    
    def test_ping(self, client):
        """Test ping endpoint returns ok."""
        response = client.get('/api/ping')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'


class TestTransformEndpoint:
    """Test the transform endpoint with various inputs."""
    
    def test_valid_transformation(self, client):
        """Test valid transformation request."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "diagnosen": [
                {
                    "icd10": "I10",
                    "beschreibung": "Hypertonie",
                    "klinischer_status": "active"
                }
            ],
            "laborwerte": [
                {
                    "loinc": "1234-5",
                    "wert": 140.0,
                    "einheit": "mg/dL",
                    "gemessen_am": "2024-01-01T10:00:00"
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
        assert data['resourceType'] == 'Bundle'
        assert data['type'] == 'collection'
        assert 'entry' in data
        assert len(data['entry']) == 3  # Patient + Condition + Observation
    
    def test_invalid_content_type(self, client):
        """Test that non-JSON content type is rejected."""
        response = client.post(
            '/api/transform',
            data="not json",
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == 'InvalidContentType'
        assert 'application/json' in data['message']
    
    def test_invalid_geschlecht(self, client):
        """Test that invalid geschlecht is rejected with proper error."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "invalid"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
        assert 'validation_errors' in data['details']
    
    def test_invalid_icd10_code(self, client):
        """Test that invalid ICD-10 code is rejected."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "diagnosen": [
                {
                    "icd10": "invalid-code",
                    "beschreibung": "Test"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
        assert 'validation_errors' in data['details']
    
    def test_invalid_ops_code(self, client):
        """Test that invalid OPS code is rejected."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "prozeduren": [
                {
                    "ops": "invalid",
                    "beschreibung": "Test"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
        assert 'validation_errors' in data['details']
    
    def test_invalid_loinc_code(self, client):
        """Test that invalid LOINC code is rejected."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            },
            "laborwerte": [
                {
                    "loinc": "invalid",
                    "wert": 100.0,
                    "einheit": "mg/dL"
                }
            ]
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
        assert 'validation_errors' in data['details']
    
    def test_future_birth_date(self, client):
        """Test that future birth date is rejected."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "2030-01-01",
                "geschlecht": "male"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
        assert 'validation_errors' in data['details']
    
    def test_empty_patient_name(self, client):
        """Test that empty patient name is rejected."""
        payload = {
            "patient": {
                "vorname": "",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "male"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
    
    def test_missing_required_fields(self, client):
        """Test that missing required fields are rejected."""
        payload = {
            "patient": {
                "vorname": "Max"
                # Missing nachname, geburtsdatum, geschlecht
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 422
        data = response.get_json()
        assert data['error'] == 'ValidationError'
    
    def test_error_response_format(self, client):
        """Test that error responses have the standard format."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1990-01-01",
                "geschlecht": "invalid"
            }
        }
        
        response = client.post(
            '/api/transform',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        data = response.get_json()
        # Check standard error response format
        assert 'error' in data
        assert 'message' in data
        assert 'timestamp' in data
        assert 'details' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
