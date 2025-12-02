"""Tests for Flask API endpoints."""

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


class TestAPI:
    """Test Flask API endpoints."""

    def test_ping_endpoint(self, client):
        """Test the ping endpoint."""
        response = client.get('/api/ping')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_transform_endpoint_success(self, client):
        """Test successful transformation."""
        payload = {
            "patient": {
                "vorname": "Max",
                "nachname": "Mustermann",
                "geburtsdatum": "1980-01-01",
                "geschlecht": "male"
            },
            "diagnosen": [
                {
                    "icd10": "E11.9",
                    "beschreibung": "Diabetes mellitus"
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
        assert len(data['entry']) == 2  # Patient + Condition

    def test_transform_endpoint_invalid_data(self, client):
        """Test transformation with invalid data."""
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
