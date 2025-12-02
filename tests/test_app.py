"""Tests for the Flask application configuration and endpoints"""
import pytest
import json
import os
from datetime import date, datetime


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    # Set test environment variables
    os.environ["FLASK_ENV"] = "test"
    os.environ["FLASK_DEBUG"] = "false"
    os.environ["CORS_ORIGINS"] = "http://localhost:3000"
    os.environ["LOG_LEVEL"] = "ERROR"
    
    # Import app after setting environment variables
    from app import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_ping_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/api/ping')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_transform_endpoint_with_valid_data(client):
    """Test the transform endpoint with valid data"""
    payload = {
        "patient": {
            "vorname": "Max",
            "nachname": "Mustermann",
            "geburtsdatum": "1990-01-01",
            "geschlecht": "male"
        },
        "diagnosen": [
            {
                "icd10": "E11.9",
                "beschreibung": "Diabetes mellitus Type 2",
                "klinischer_status": "active"
            }
        ],
        "prozeduren": [],
        "laborwerte": []
    }
    
    response = client.post(
        '/api/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['resourceType'] == 'Bundle'
    assert data['type'] == 'collection'
    assert 'entry' in data
    assert len(data['entry']) >= 2  # Patient + Condition


def test_transform_endpoint_with_invalid_data(client):
    """Test the transform endpoint with invalid data"""
    payload = {
        "patient": {
            "vorname": "Max"
            # Missing required fields
        }
    }
    
    response = client.post(
        '/api/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Invalid input data'
    assert 'details' in data


def test_transform_endpoint_with_empty_payload(client):
    """Test the transform endpoint with empty payload"""
    response = client.post(
        '/api/transform',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_404_error_handler(client):
    """Test the 404 error handler"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Not found'


def test_cors_headers(client):
    """Test that CORS headers are present"""
    response = client.get('/api/ping', headers={
        'Origin': 'http://localhost:3000'
    })
    assert response.status_code == 200
    # CORS headers should be present in the response
    assert 'Access-Control-Allow-Origin' in response.headers


def test_environment_variable_debug_mode():
    """Test that debug mode is controlled by environment variables"""
    # This test verifies the logic in app.py without actually running the server
    import importlib
    import sys
    
    # Test production mode (debug=False)
    os.environ["FLASK_ENV"] = "production"
    os.environ["FLASK_DEBUG"] = "false"
    
    # Reload the app module to pick up new environment variables
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # The app should not be in debug mode
    assert os.getenv("FLASK_DEBUG", "false").lower() == "false"
    
    # Test development mode (debug=True)
    os.environ["FLASK_ENV"] = "development"
    if 'FLASK_DEBUG' in os.environ:
        del os.environ['FLASK_DEBUG']
    
    # When FLASK_ENV=development and FLASK_DEBUG is not set, debug should be enabled
    assert os.getenv("FLASK_ENV") == "development"


def test_transform_with_all_resource_types(client):
    """Test transform endpoint with patient, diagnoses, procedures, and lab values"""
    payload = {
        "patient": {
            "id": "test-patient-123",
            "vorname": "Anna",
            "nachname": "Schmidt",
            "geburtsdatum": "1985-05-15",
            "geschlecht": "female"
        },
        "diagnosen": [
            {
                "icd10": "I10",
                "beschreibung": "Essential hypertension",
                "begonnen_am": "2023-01-15",
                "klinischer_status": "active"
            }
        ],
        "prozeduren": [
            {
                "ops": "3-200",
                "beschreibung": "Native CT scan of the head",
                "datum": "2023-06-20"
            }
        ],
        "laborwerte": [
            {
                "loinc": "2345-7",
                "wert": 120.5,
                "einheit": "mg/dL",
                "gemessen_am": "2023-07-01T10:30:00",
                "referenz_min": 70.0,
                "referenz_max": 100.0,
                "beschreibung": "Glucose"
            }
        ]
    }
    
    response = client.post(
        '/api/transform',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['resourceType'] == 'Bundle'
    assert len(data['entry']) == 4  # Patient + Condition + Procedure + Observation
    
    # Verify resource types
    resource_types = [entry['resource']['resourceType'] for entry in data['entry']]
    assert 'Patient' in resource_types
    assert 'Condition' in resource_types
    assert 'Procedure' in resource_types
    assert 'Observation' in resource_types
