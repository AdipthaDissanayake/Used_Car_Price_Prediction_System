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


def test_normal_user_register_and_login(client):
    unique_email = "testrunner_user@it3051.org"
    # Register
    reg_payload = {
        'name': 'Test Runner',
        'email': unique_email,
        'password': 'securepassword123'
    }
    res_reg = client.post('/api/auth/register', data=json.dumps(reg_payload), content_type='application/json')
    assert res_reg.status_code in (201, 400)

    # Login
    login_payload = {
        'email': unique_email,
        'password': 'securepassword123'
    }
    res_login = client.post('/api/auth/login', data=json.dumps(login_payload), content_type='application/json')
    assert res_login.status_code == 200
    data = res_login.get_json()
    assert data['status'] == 'success'
    assert 'token' in data
    assert data['user']['email'] == unique_email

    # Wrong password test
    bad_login = client.post('/api/auth/login', data=json.dumps({'email': unique_email, 'password': 'wrong'}), content_type='application/json')
    assert bad_login.status_code == 401


def test_user_history_and_deletion(client):
    # 1. Login user to get token
    login_res = client.post('/api/auth/login', data=json.dumps({
        'email': 'testrunner_user@it3051.org',
        'password': 'securepassword123'
    }), content_type='application/json')
    token = login_res.get_json()['token']
    auth_headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # 2. Make prediction under this user
    car_payload = {
        'brand': 'BMW',
        'model_year': 2022,
        'milage': 25000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }
    pred_res = client.post('/predict', data=json.dumps(car_payload), headers=auth_headers)
    assert pred_res.status_code == 200
    log_id = pred_res.get_json()['data'].get('log_id')
    assert log_id is not None

    # 3. Query user history
    hist_res = client.get('/api/predictions/history', headers=auth_headers)
    assert hist_res.status_code == 200
    history = hist_res.get_json()['data']
    assert any(h['id'] == log_id for h in history)

    # 4. Delete single prediction
    del_res = client.delete(f'/api/predictions/history/{log_id}', headers=auth_headers)
    assert del_res.status_code == 200

    # Verify deleted
    hist_after = client.get('/api/predictions/history', headers=auth_headers).get_json()['data']
    assert not any(h['id'] == log_id for h in hist_after)

    # 5. Clear all history test
    clear_res = client.delete('/api/predictions/history', headers=auth_headers)
    assert clear_res.status_code == 200
    hist_empty = client.get('/api/predictions/history', headers=auth_headers).get_json()['data']
    assert len(hist_empty) == 0
