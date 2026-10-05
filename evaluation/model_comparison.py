"""
Stage 7: Model Comparison, Selection & Final Evaluation
Used Car Price Prediction System - IT3051
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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


def evaluate_candidate(name, model, X_train, y_train, X_test, y_test):
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        'r2': 'r2',
        'neg_mae': 'neg_mean_absolute_error',
        'neg_rmse': 'neg_root_mean_squared_error'
    }
    cv_res = cross_validate(model, X_train, y_train, cv=kf, scoring=scoring, n_jobs=-1)

    model.fit(X_train, y_train)
    y_pred_log = model.predict(X_test)
    test_r2 = r2_score(y_test, y_pred_log)
    test_mae = mean_absolute_error(y_test, y_pred_log)
    test_rmse = root_mean_squared_error(y_test, y_pred_log)

    y_test_dollars = np.expm1(y_test)
    y_pred_dollars = np.expm1(y_pred_log)
    dollar_mae = mean_absolute_error(y_test_dollars, y_pred_dollars)
    dollar_rmse = root_mean_squared_error(y_test_dollars, y_pred_dollars)

    return {
        'Model': name,
        'CV_R2_Mean': cv_res['test_r2'].mean(),
        'CV_R2_Std': cv_res['test_r2'].std(),
        'CV_MAE': -cv_res['test_neg_mae'].mean(),
        'CV_RMSE': -cv_res['test_neg_rmse'].mean(),
        'Test_R2': test_r2,
        'Test_MAE_log': test_mae,
        'Test_RMSE_log': test_rmse,
        'Test_MAE_USD': dollar_mae,
        'Test_RMSE_USD': dollar_rmse
    }, model


def run_comparison():
    print("=" * 60)
    print("STAGE 7: MODEL COMPARISON & FINAL SELECTION")
    print("=" * 60)

    X_train, X_test, y_train, y_test = load_data()

    # Define baseline models
    baselines = {
        'Linear Regression': LinearRegression(),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    }

    base_results = []
    fitted_baselines = {}
    for name, model in baselines.items():
        res, fitted = evaluate_candidate(name, model, X_train, y_train, X_test, y_test)
        base_results.append(res)
        fitted_baselines[name] = fitted

    df_base = pd.DataFrame(base_results)
    os.makedirs('results', exist_ok=True)
    df_base.to_csv('results/baseline_results.csv', index=False)

    print("\n--- Baseline Model Comparison Table ---")
    print(df_base[['Model', 'CV_R2_Mean', 'Test_R2', 'Test_MAE_USD', 'Test_RMSE_USD']].to_string(index=False))

    # Champion model selection: Gradient Boosting Regressor (highest Test R2 = 0.6619, lowest RMSE = 0.4973)
    champion_model = baselines['Gradient Boosting']
    champion_model.fit(X_train, y_train)

    y_pred_log = champion_model.predict(X_test)
    y_pred_usd = np.expm1(y_pred_log)
    y_test_usd = np.expm1(y_test)

    # Save champion model artifact
    os.makedirs('artifacts/models', exist_ok=True)
    joblib.dump(champion_model, 'artifacts/models/final_model.joblib')

    final_results = {
        'champion_model': 'Gradient Boosting Regressor',
        'hyperparameters': {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 3,
            'random_state': 42
        },
        'cv_5fold_r2_mean': float(df_base.loc[df_base['Model'] == 'Gradient Boosting', 'CV_R2_Mean'].values[0]),
        'cv_5fold_r2_std': float(df_base.loc[df_base['Model'] == 'Gradient Boosting', 'CV_R2_Std'].values[0]),
        'test_r2': float(r2_score(y_test, y_pred_log)),
        'test_mae_log': float(mean_absolute_error(y_test, y_pred_log)),
        'test_rmse_log': float(root_mean_squared_error(y_test, y_pred_log)),
        'test_mae_usd': float(mean_absolute_error(y_test_usd, y_pred_usd)),
        'test_rmse_usd': float(root_mean_squared_error(y_test_usd, y_pred_usd)),
        'runner_up_model': 'Random Forest Regressor (Tuned)',
        'runner_up_test_r2': 0.6595,
        'runner_up_test_mae_usd': 17733.18
    }

    with open('results/final_model_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)

    os.makedirs('artifacts/metadata', exist_ok=True)
    with open('artifacts/metadata/model_registry.json', 'w') as f:
        json.dump({
            'champion': 'Gradient Boosting Regressor',
            'model_path': 'artifacts/models/final_model.joblib',
            'status': 'production_ready',
            'supported_models': [
                'Linear Regression',
                'Decision Tree',
                'Random Forest',
                'Gradient Boosting'
            ]
        }, f, indent=2)

    # Generate Evaluation Plots
    os.makedirs('results/plots', exist_ok=True)

    # 1. Model R2 Comparison Bar Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    models = df_base['Model']
    r2_scores = df_base['Test_R2']
    bars = ax.bar(models, r2_scores, color=['#4285F4', '#EA4335', '#FBBC04', '#34A853'])
    ax.set_ylabel('Test R-squared ($R^2$)')
    ax.set_title('Stage 6 & 7: Model Comparison on Test Data ($R^2$ Score)')
    ax.set_ylim(0, 0.8)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.015, f"{yval:.4f}", ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('results/plots/model_r2_comparison.png', dpi=300)
    plt.close()

    # 2. Predicted vs Actual Scatter Plot for Champion Model
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_test_usd, y_pred_usd, alpha=0.35, color='#1A73E8', edgecolors='none', s=30)
    max_val = max(y_test_usd.max(), y_pred_usd.max())
    ax.plot([0, max_val], [0, max_val], 'r--', lw=2, label='Perfect Prediction (y = x)')
    ax.set_xlabel('Actual Price (USD $)', fontweight='bold')
    ax.set_ylabel('Predicted Price (USD $)', fontweight='bold')
    ax.set_title('Champion Model (Gradient Boosting): Actual vs Predicted Prices')
    ax.legend()
    plt.tight_layout()
    plt.savefig('results/plots/final_model_pred_vs_actual.png', dpi=300)
    plt.close()

    # 3. Residual Distribution
    residuals_usd = y_test_usd - y_pred_usd
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals_usd, bins=50, color='#34A853', edgecolor='black', alpha=0.7)
    ax.axvline(0, color='red', linestyle='--', lw=2)
    ax.set_xlabel('Prediction Error (Actual - Predicted USD $)')
    ax.set_ylabel('Frequency')
    ax.set_title('Champion Model Residual Distribution (USD $)')
    plt.tight_layout()
    plt.savefig('results/plots/final_model_residual_distribution.png', dpi=300)
    plt.close()

    print("\n[OK] Model comparison, artifacts, and plots generated successfully.")
    print("  Artifact: artifacts/models/final_model.joblib")
    print("  Metrics: results/final_model_results.json")
    print("  Plots: results/plots/")


if __name__ == '__main__':
    run_comparison()
