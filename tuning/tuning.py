"""
Stage 7: Hyperparameter Tuning Pipeline
Used Car Price Prediction System - IT3051

Evaluates and compares tuned configurations for:
- Decision Tree
- Random Forest
- Gradient Boosting
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
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


def evaluate_spec(model, X_train, y_train, X_test, y_test, model_name, variant, params_desc):
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
        'Model': model_name,
        'Variant': variant,
        'Parameters': params_desc,
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


def run_tuning():
    print("=" * 60)
    print("STAGE 7: HYPERPARAMETER TUNING EXPERIMENTS")
    print("=" * 60)

    X_train, X_test, y_train, y_test = load_data()

    experiments = []

    # 1. Linear Regression (Baseline benchmark)
    experiments.append(evaluate_spec(
        LinearRegression(), X_train, y_train, X_test, y_test,
        'Linear Regression', 'Baseline', 'default'
    ))

    # 2. Decision Tree variants
    experiments.append(evaluate_spec(
        DecisionTreeRegressor(random_state=42), X_train, y_train, X_test, y_test,
        'Decision Tree', 'Baseline', 'default (unconstrained)'
    ))
    experiments.append(evaluate_spec(
        DecisionTreeRegressor(max_depth=6, min_samples_leaf=15, max_features=0.8, random_state=42),
        X_train, y_train, X_test, y_test,
        'Decision Tree', 'Tuned', 'max_depth=6, min_samples_leaf=15, max_features=0.8'
    ))

    # 3. Random Forest variants
    experiments.append(evaluate_spec(
        RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test,
        'Random Forest', 'Baseline', 'n_estimators=100, default'
    ))
    experiments.append(evaluate_spec(
        RandomForestRegressor(n_estimators=100, max_depth=18, max_features='sqrt', min_samples_leaf=4, random_state=42, n_jobs=-1),
        X_train, y_train, X_test, y_test,
        'Random Forest', 'Tuned', 'n=100, max_depth=18, max_features=sqrt, min_samples_leaf=4'
    ))

    # 4. Gradient Boosting variants
    experiments.append(evaluate_spec(
        GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42),
        X_train, y_train, X_test, y_test,
        'Gradient Boosting', 'Baseline', 'n=100, lr=0.1, max_depth=3'
    ))
    experiments.append(evaluate_spec(
        GradientBoostingRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, subsample=0.85, random_state=42),
        X_train, y_train, X_test, y_test,
        'Gradient Boosting', 'Tuned', 'n=150, lr=0.05, max_depth=4, subsample=0.85'
    ))

    df_exp = pd.DataFrame(experiments)
    os.makedirs('results', exist_ok=True)
    df_exp.to_csv('results/experiment_log.csv', index=False)

    df_tuned = df_exp[df_exp['Variant'] == 'Tuned'].copy()
    df_tuned.to_csv('results/tuned_results.csv', index=False)

    print("\n--- Hyperparameter Tuning Results ---")
    print(df_exp[['Model', 'Variant', 'CV_R2_Mean', 'Test_R2', 'Test_MAE_USD', 'Test_RMSE_USD']].to_string(index=False))

    return df_exp


if __name__ == '__main__':
    run_tuning()
