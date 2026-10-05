"""
Stage 6: Linear Regression Model Implementation
Used Car Price Prediction System - IT3051
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error


def load_data():
    """Load preprocessed datasets."""
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


def run_linear_regression():
    print("=" * 60)
    print("STAGE 6: LINEAR REGRESSION BASELINE")
    print("=" * 60)

    X_train, X_test, y_train, y_test = load_data()

    # Model definition
    model = LinearRegression()

    # 5-fold Cross-Validation on training set
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        'r2': 'r2',
        'neg_mae': 'neg_mean_absolute_error',
        'neg_rmse': 'neg_root_mean_squared_error'
    }
    cv_res = cross_validate(model, X_train, y_train, cv=kf, scoring=scoring)

    cv_r2_mean = cv_res['test_r2'].mean()
    cv_r2_std = cv_res['test_r2'].std()
    cv_mae_mean = -cv_res['test_neg_mae'].mean()
    cv_rmse_mean = -cv_res['test_neg_rmse'].mean()

    # Fit on entire training set
    model.fit(X_train, y_train)

    # Test set evaluation
    y_pred_log = model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred_log)
    test_mae = mean_absolute_error(y_test, y_pred_log)
    test_rmse = root_mean_squared_error(y_test, y_pred_log)

    # Dollar scale evaluation
    y_test_dollars = np.expm1(y_test)
    y_pred_dollars = np.expm1(y_pred_log)
    dollar_mae = mean_absolute_error(y_test_dollars, y_pred_dollars)
    dollar_rmse = root_mean_squared_error(y_test_dollars, y_pred_dollars)

    print("\n--- Model Performance Summary ---")
    print(f"5-Fold CV R2   : {cv_r2_mean:.4f} +/- {cv_r2_std:.4f}")
    print(f"5-Fold CV MAE  : {cv_mae_mean:.4f}")
    print(f"5-Fold CV RMSE : {cv_rmse_mean:.4f}")
    print(f"Test Set R2    : {test_r2:.4f}")
    print(f"Test Set MAE   : {test_mae:.4f} (log) | ${dollar_mae:,.2f}")
    print(f"Test Set RMSE  : {test_rmse:.4f} (log) | ${dollar_rmse:,.2f}")

    # Coefficients
    coef_df = pd.DataFrame({
        'Feature': X_train.columns,
        'Coefficient': model.coef_
    }).sort_values('Coefficient', key=abs, ascending=False)
    print("\nTop 5 Coefficients:")
    print(coef_df.head(5).to_string(index=False))

    # Save artifacts
    os.makedirs('artifacts/models', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    joblib.dump(model, 'artifacts/models/linear_regression.joblib')

    metrics_df = pd.DataFrame([{
        'Model': 'Linear Regression',
        'Variant': 'Baseline',
        'CV_R2_Mean': cv_r2_mean,
        'CV_R2_Std': cv_r2_std,
        'CV_MAE': cv_mae_mean,
        'CV_RMSE': cv_rmse_mean,
        'Test_R2': test_r2,
        'Test_MAE_log': test_mae,
        'Test_RMSE_log': test_rmse,
        'Test_MAE_USD': dollar_mae,
        'Test_RMSE_USD': dollar_rmse
    }])
    metrics_df.to_csv('results/linear_regression_metrics.csv', index=False)

    return model, metrics_df


if __name__ == '__main__':
    run_linear_regression()
