"""
End-to-End System Tests and Domain Sanity Checks
"""

import os
import sys
import json
import pytest
import pandas as pd

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_end_to_end_luxury_vs_economy(client):
    """Under identical year and mileage, luxury brand must predict higher price than economy."""
    luxury_car = {
        'brand': 'Porsche',
        'model_year': 2022,
        'milage': 20000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    economy_car = {
        'brand': 'Toyota',
        'model_year': 2022,
        'milage': 20000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    res_lux = client.post('/predict', data=json.dumps(luxury_car), content_type='application/json')
    res_eco = client.post('/predict', data=json.dumps(economy_car), content_type='application/json')

    assert res_lux.status_code == 200
    assert res_eco.status_code == 200

    price_lux = res_lux.get_json()['data']['predicted_price']
    price_eco = res_eco.get_json()['data']['predicted_price']

    assert price_lux > price_eco, f"Expected Porsche ({price_lux}) > Toyota ({price_eco})"


def test_end_to_end_mileage_depreciation(client):
    """Lower mileage must yield a higher valuation than high mileage for same model and year."""
    low_miles = {
        'brand': 'Honda',
        'model_year': 2020,
        'milage': 15000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    high_miles = {
        'brand': 'Honda',
        'model_year': 2020,
        'milage': 140000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    res_low = client.post('/predict', data=json.dumps(low_miles), content_type='application/json')
    res_high = client.post('/predict', data=json.dumps(high_miles), content_type='application/json')

    assert res_low.status_code == 200
    assert res_high.status_code == 200

    price_low = res_low.get_json()['data']['predicted_price']
    price_high = res_high.get_json()['data']['predicted_price']

    assert price_low > price_high, f"Expected Low Mileage ({price_low}) > High Mileage ({price_high})"


def test_end_to_end_accident_impact(client):
    """Vehicle with clean history must yield higher or equal valuation than one with damage reported."""
    clean_car = {
        'brand': 'BMW',
        'model_year': 2021,
        'milage': 35000,
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    damaged_car = {
        'brand': 'BMW',
        'model_year': 2021,
        'milage': 35000,
        'transmission': 'Automatic',
        'clean_title': 'No',
        'accident': 'At least 1 accident or damage reported',
        'fuel_type': 'Gasoline'
    }

    res_clean = client.post('/predict', data=json.dumps(clean_car), content_type='application/json')
    res_damaged = client.post('/predict', data=json.dumps(damaged_car), content_type='application/json')

    price_clean = res_clean.get_json()['data']['predicted_price']
    price_damaged = res_damaged.get_json()['data']['predicted_price']

    assert price_clean > price_damaged, f"Expected Clean History ({price_clean}) > Damaged History ({price_damaged})"
