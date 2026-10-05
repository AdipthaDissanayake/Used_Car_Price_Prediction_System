"""
Stage 6 & 7: Decision Tree Regressor Implementation & Tuning
Used Car Price Prediction System - IT3051
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import KFold, cross_validate, GridSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error


def load_data():
    if os.path.exists('data/processed/X_train.csv'):
        X_train = pd.read_csv('data/processed/X_train.csv')
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_train = pd.read_csv('data/processed/y_train.csv').values.ravel()
        y_test = pd.read_csv('data/processed/y_test.csv').values.ravel()
    else:
        X_train = pd.read_csv('X_train.csv')
        X_test = pd.read_csv('X_test.csv')
        y_train = pd.read_csv('y_train.csv').values.ravel()
        y_test = pd.read_csv('y_test.csv').values.ravel()
    return X_train, X_test, y_train, y_test


def evaluate_model(model, X_train, y_train, X_test, y_test, model_name, variant):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        'r2': 'r2',
        'neg_mae': 'neg_mean_absolute_error',
        'neg_rmse': 'neg_root_mean_squared_error'
    }
    cv_res = cross_validate(model, X_train, y_train, cv=kf, scoring=scoring)

    model.fit(X_train, y_train)
    y_pred_log = model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred_log)
    test_mae = mean_absolute_error(y_test, y_pred_log)
    test_rmse = root_mean_squared_error(y_test, y_pred_log)

    y_test_dollars = np.expm1(y_test)
    y_pred_dollars = np.expm1(y_pred_log)
    dollar_mae = mean_absolute_error(y_test_dollars, y_pred_dollars)
    dollar_rmse = root_mean_squared_error(y_test_dollars, y_pred_dollars)

    metrics = {
        'Model': model_name,
        'Variant': variant,
        'CV_R2_Mean': cv_res['test_r2'].mean(),
        'CV_R2_Std': cv_res['test_r2'].std(),
        'CV_MAE': -cv_res['test_neg_mae'].mean(),
        'CV_RMSE': -cv_res['test_neg_rmse'].mean(),
        'Test_R2': test_r2,
        'Test_MAE_log': test_mae,
        'Test_RMSE_log': test_rmse,
        'Test_MAE_USD': dollar_mae,
        'Test_RMSE_USD': dollar_rmse
    }
    return metrics, model


def run_decision_tree():
    print("=" * 60)
    print("STAGE 6 & 7: DECISION TREE REGRESSOR")
    print("=" * 60)

    X_train, X_test, y_train, y_test = load_data()

    # 1. Baseline Decision Tree (Unconstrained)
    base_model = DecisionTreeRegressor(random_state=42)
    base_metrics, base_fitted = evaluate_model(
        base_model, X_train, y_train, X_test, y_test, 'Decision Tree', 'Baseline (Default)'
    )

    print("\n--- Baseline Decision Tree Performance ---")
    print(f"5-Fold CV R2   : {base_metrics['CV_R2_Mean']:.4f} +/- {base_metrics['CV_R2_Std']:.4f}")
    print(f"Test Set R2    : {base_metrics['Test_R2']:.4f}")
    print(f"Test Set MAE   : {base_metrics['Test_MAE_log']:.4f} (log) | ${base_metrics['Test_MAE_USD']:,.2f}")

    # 2. Tuned Decision Tree (Regularized)
    tuned_model = DecisionTreeRegressor(
        max_depth=6,
        min_samples_leaf=15,
        max_features=0.8,
        random_state=42
    )
    tuned_metrics, tuned_fitted = evaluate_model(
        tuned_model, X_train, y_train, X_test, y_test, 'Decision Tree', 'Tuned (Regularized)'
    )

    print("\n--- Tuned Decision Tree Performance ---")
    print(f"5-Fold CV R2   : {tuned_metrics['CV_R2_Mean']:.4f} +/- {tuned_metrics['CV_R2_Std']:.4f}")
    print(f"Test Set R2    : {tuned_metrics['Test_R2']:.4f}")
    print(f"Test Set MAE   : {tuned_metrics['Test_MAE_log']:.4f} (log) | ${tuned_metrics['Test_MAE_USD']:,.2f}")

    # Feature Importance
    feat_imp = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': tuned_fitted.feature_importances_
    }).sort_values('Importance', ascending=False)
    print("\nTuned DT Feature Importances:")
    print(feat_imp.head(5).to_string(index=False))

    # Save artifacts
    os.makedirs('artifacts/models', exist_ok=True)
    os.makedirs('results/feature_importance', exist_ok=True)
    joblib.dump(tuned_fitted, 'artifacts/models/decision_tree.joblib')
    feat_imp.to_csv('results/feature_importance/dt_feature_importance.csv', index=False)

    df_results = pd.DataFrame([base_metrics, tuned_metrics])
    df_results.to_csv('results/decision_tree_metrics.csv', index=False)

    return tuned_fitted, df_results


if __name__ == '__main__':
    run_decision_tree()
