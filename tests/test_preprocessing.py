"""
Tests for Data Preprocessing and Leakage Prevention
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from preprocessing.preprocessing import CarDataPreprocessor, FEATURE_COLUMNS, CONTINUOUS_COLUMNS


@pytest.fixture
def datasets():
    train_path = os.path.join(repo_root, 'data', 'processed', 'X_train.csv')
    test_path = os.path.join(repo_root, 'data', 'processed', 'X_test.csv')
    y_train_path = os.path.join(repo_root, 'data', 'processed', 'y_train.csv')
    y_test_path = os.path.join(repo_root, 'data', 'processed', 'y_test.csv')

    if not os.path.exists(train_path):
        train_path = os.path.join(repo_root, 'X_train.csv')
        test_path = os.path.join(repo_root, 'X_test.csv')
        y_train_path = os.path.join(repo_root, 'y_train.csv')
        y_test_path = os.path.join(repo_root, 'y_test.csv')

    X_train = pd.read_csv(train_path)
    X_test = pd.read_csv(test_path)
    y_train = pd.read_csv(y_train_path).values.ravel()
    y_test = pd.read_csv(y_test_path).values.ravel()

    return X_train, X_test, y_train, y_test


def test_split_dimensions(datasets):
    X_train, X_test, y_train, y_test = datasets
    assert len(X_train) == 3206, f"Expected 3,206 training rows, got {len(X_train)}"
    assert len(X_test) == 802, f"Expected 802 testing rows, got {len(X_test)}"
    assert len(y_train) == 3206
    assert len(y_test) == 802
    assert X_train.shape[1] == 13, f"Expected 13 features, got {X_train.shape[1]}"
    assert X_test.shape[1] == 13


def test_no_missing_values(datasets):
    X_train, X_test, y_train, y_test = datasets
    assert X_train.isnull().sum().sum() == 0, "X_train contains NaN values"
    assert X_test.isnull().sum().sum() == 0, "X_test contains NaN values"
    assert np.isnan(y_train).sum() == 0, "y_train contains NaN values"
    assert np.isnan(y_test).sum() == 0, "y_test contains NaN values"


def test_feature_columns_exact_match(datasets):
    X_train, X_test, _, _ = datasets
    assert list(X_train.columns) == FEATURE_COLUMNS
    assert list(X_test.columns) == FEATURE_COLUMNS
    assert 'log_price' not in X_train.columns
    assert 'price' not in X_train.columns


def test_leakage_prevention(datasets):
    X_train, X_test, _, _ = datasets
    for col in CONTINUOUS_COLUMNS:
        train_mean = X_train[col].mean()
        train_std = X_train[col].std()
        assert abs(train_mean) < 1e-4, f"Training mean for {col} is {train_mean}, expected ~0"
        assert abs(train_std - 1.0) < 1e-4, f"Training std for {col} is {train_std}, expected ~1"


def test_preprocessor_single_transform():
    preprocessor = CarDataPreprocessor()
    # Mock fitted stats
    preprocessor.means = {'car_age': 8.0, 'milage': 60000.0, 'mileage_per_year': 7500.0}
    preprocessor.stds = {'car_age': 4.0, 'milage': 30000.0, 'mileage_per_year': 3500.0}

    sample_car = {
        'model_year': 2021,
        'milage': 35000,
        'brand': 'BMW',
        'transmission': 'Automatic',
        'clean_title': 'Yes',
        'accident': 'None reported',
        'fuel_type': 'Gasoline'
    }

    df_trans = preprocessor.transform_single(sample_car)
    assert df_trans.shape == (1, 13)
    assert df_trans['is_luxury_brand'].iloc[0] == 1
    assert df_trans['is_clean_title'].iloc[0] == 1
    assert df_trans['has_accident'].iloc[0] == 0
    assert df_trans['fuel_Gasoline'].iloc[0] == 1
    assert df_trans.isnull().sum().sum() == 0
