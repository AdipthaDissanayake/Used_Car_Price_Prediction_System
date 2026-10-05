"""
Tests for Flask REST API Backend Endpoints and Error Handling
"""

import os
import sys
import json
import pytest

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert 'model' in data
    assert 'version' in data


def test_metadata_endpoint(client):
    res = client.get('/metadata')
    assert res.status_code == 200
    data = res.get_json()
    assert 'luxury_brands' in data
    assert 'valid_fuel_types' in data


def test_predict_valid_payload(client):
    payload = {
        'brand': 'Toyota',
        'model_year': 2021,
        'milage': 32000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }
    res = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    pred = data['data']
    assert 'predicted_price' in pred
    assert pred['predicted_price'] > 5000
    assert 'predicted_price_formatted' in pred
    assert 'price_range_90_pct' in pred
    assert 'insights' in pred


def test_predict_invalid_year_out_of_range(client):
    payload = {
        'brand': 'Toyota',
        'model_year': 1850,  # invalid
        'milage': 32000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }
    res = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 422
    data = res.get_json()
    assert 'error' in data


def test_predict_negative_mileage(client):
    payload = {
        'brand': 'Toyota',
        'model_year': 2020,
        'milage': -500,  # invalid
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }
    res = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 422


def test_predict_missing_fields(client):
    payload = {
        'brand': 'Toyota',
        # missing model_year, milage, etc.
    }
    res = client.post('/predict', data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 400


def test_google_auth_endpoint(client):
    auth_payload = {
        'user': {
            'sub': 'google_test_sub_999',
            'email': 'driver@test.com',
            'name': 'Test Driver',
            'picture': 'https://example.com/driver.png'
        }
    }
    res = client.post('/api/auth/google', data=json.dumps(auth_payload), content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['user']['email'] == 'driver@test.com'


def test_prediction_history_endpoint(client):
    res = client.get('/api/predictions/history?limit=5')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'data' in data
