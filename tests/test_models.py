"""
Tests for Machine Learning Models and Predictions
"""

import os
import sys
import pytest
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


@pytest.fixture
def test_data():
    test_path = os.path.join(repo_root, 'data', 'processed', 'X_test.csv')
    y_test_path = os.path.join(repo_root, 'data', 'processed', 'y_test.csv')
    if not os.path.exists(test_path):
        test_path = os.path.join(repo_root, 'X_test.csv')
        y_test_path = os.path.join(repo_root, 'y_test.csv')

    X_test = pd.read_csv(test_path)
    y_test = pd.read_csv(y_test_path).values.ravel()
    return X_test, y_test


def test_final_model_artifact_exists():
    path = os.path.join(repo_root, 'artifacts', 'models', 'final_model.joblib')
    assert os.path.exists(path), f"Champion model not found at {path}"


def test_champion_model_performance(test_data):
    X_test, y_test = test_data
    model_path = os.path.join(repo_root, 'artifacts', 'models', 'final_model.joblib')
    model = joblib.load(model_path)

    y_pred_log = model.predict(X_test)
    r2 = r2_score(y_test, y_pred_log)

    # Champion model must achieve Test R2 > 0.65
    assert r2 > 0.65, f"Expected Champion Model Test R2 > 0.65, got {r2:.4f}"

    # Price values inverted from log scale must be positive
    y_pred_usd = np.expm1(y_pred_log)
    assert np.all(y_pred_usd > 0), "Predicted prices must all be positive"
    assert np.all(np.isfinite(y_pred_usd)), "Predicted prices must be finite"


@pytest.mark.parametrize("model_filename,min_r2", [
    ("linear_regression.joblib", 0.58),
    ("decision_tree.joblib", 0.60),
    ("random_forest.joblib", 0.64),
    ("gradient_boosting.joblib", 0.65)
])
def test_all_saved_models_predict(test_data, model_filename, min_r2):
    X_test, y_test = test_data
    path = os.path.join(repo_root, 'artifacts', 'models', model_filename)
    assert os.path.exists(path), f"Model file {model_filename} is missing"

    model = joblib.load(path)
    preds = model.predict(X_test)
    score = r2_score(y_test, preds)
    assert score >= min_r2, f"Model {model_filename} scored R2 {score:.4f}, below expected {min_r2}"
