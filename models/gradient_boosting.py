"""
Stage 6 & 7: Gradient Boosting Regressor Implementation & Tuning
Used Car Price Prediction System - IT3051
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_validate
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


def run_gradient_boosting():
    print("=" * 60)
    print("STAGE 6 & 7: GRADIENT BOOSTING REGRESSOR")
    print("=" * 60)

    X_train, X_test, y_train, y_test = load_data()

    # 1. Baseline Gradient Boosting
    gb_base = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    base_metrics, base_fitted = evaluate_model(
        gb_base, X_train, y_train, X_test, y_test, 'Gradient Boosting', 'Baseline (n=100, lr=0.1, depth=3)'
    )

    print("\n--- Baseline Gradient Boosting Performance ---")
    print(f"5-Fold CV R2   : {base_metrics['CV_R2_Mean']:.4f} +/- {base_metrics['CV_R2_Std']:.4f}")
    print(f"Test Set R2    : {base_metrics['Test_R2']:.4f}")
    print(f"Test Set MAE   : {base_metrics['Test_MAE_log']:.4f} (log) | ${base_metrics['Test_MAE_USD']:,.2f}")
    print(f"Test Set RMSE  : {base_metrics['Test_RMSE_log']:.4f} (log) | ${base_metrics['Test_RMSE_USD']:,.2f}")

    # 2. Tuned Gradient Boosting
    gb_tuned = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.85,
        random_state=42
    )
    tuned_metrics, tuned_fitted = evaluate_model(
        gb_tuned, X_train, y_train, X_test, y_test, 'Gradient Boosting', 'Tuned (n=150, lr=0.05, depth=4, subsample=0.85)'
    )

    print("\n--- Tuned Gradient Boosting Performance ---")
    print(f"5-Fold CV R2   : {tuned_metrics['CV_R2_Mean']:.4f} +/- {tuned_metrics['CV_R2_Std']:.4f}")
    print(f"Test Set R2    : {tuned_metrics['Test_R2']:.4f}")
    print(f"Test Set MAE   : {tuned_metrics['Test_MAE_log']:.4f} (log) | ${tuned_metrics['Test_MAE_USD']:,.2f}")

    # Feature Importance
    feat_imp = pd.DataFrame({
        'Feature': X_train.columns,
        'Importance': base_fitted.feature_importances_
    }).sort_values('Importance', ascending=False)
    print("\nGradient Boosting Feature Importances:")
    print(feat_imp.to_string(index=False))

    # Save artifacts
    os.makedirs('artifacts/models', exist_ok=True)
    os.makedirs('results/feature_importance', exist_ok=True)
    joblib.dump(base_fitted, 'artifacts/models/gradient_boosting.joblib')
    feat_imp.to_csv('results/feature_importance/gb_feature_importance.csv', index=False)

    df_results = pd.DataFrame([base_metrics, tuned_metrics])
    df_results.to_csv('results/gradient_boosting_metrics.csv', index=False)

    return base_fitted, df_results


if __name__ == '__main__':
    run_gradient_boosting()
