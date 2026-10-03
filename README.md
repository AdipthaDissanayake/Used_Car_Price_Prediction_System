# Used Car Price Prediction System
## IT3051 – Fundamentals of Data Mining & Machine Learning (Mini Project 2026)

Predict used car market selling prices using regression models.

Target Variable: `log_price` (log-transformed selling price using \(\log(1 + \text{price})\)).

---

## 1. Project Architecture & Directory Structure

```text
Used_Car_Price_Prediction_System/
│
├── data/
│   ├── raw/
│   │   └── used_cars.csv            # Original raw dataset (4,009 rows x 12 cols)
│   └── processed/
│       ├── X_train.csv             # Training features (3,206 rows x 13 cols)
│       ├── X_test.csv              # Testing features (802 rows x 13 cols)
│       ├── y_train.csv             # Training target (3,206 rows)
│       └── y_test.csv              # Testing target (802 rows)
│
├── preprocessing/
│   └── preprocessing.py            # Single source of truth for cleaning & feature pipeline
│
├── models/
│   ├── linear_regression.py        # Model 1: Linear Regression (OLS baseline)
│   ├── decision_tree.py            # Model 2: Decision Tree Regressor (baseline & tuned)
│   ├── random_forest.py            # Model 3: Random Forest Regressor (baseline, tuned, selection)
│   └── gradient_boosting.py        # Model 4: Gradient Boosting Regressor (baseline & tuned)
│
├── evaluation/
│   └── model_comparison.py         # Cross-model evaluation, experiment log, plots, final selection
│
├── results/
│   ├── baseline_results.csv        # Baseline metrics across all 4 models
│   ├── tuned_results.csv           # Tuned metrics across all models
│   ├── experiment_log.csv          # Comprehensive experiment log (EXP_01 to EXP_08)
│   ├── feature_importance/
│   │   ├── random_forest_importance.csv
│   │   ├── gradient_boosting_importance.csv
│   │   └── decision_tree_importance.csv
│   └── plots/
│       ├── model_r2_comparison.png
│       ├── model_mae_comparison.png
│       ├── model_rmse_comparison.png
│       ├── rf_feature_importance.png
│       ├── final_model_actual_vs_predicted.png
│       └── final_model_residuals.png
│
└── README.md                       # Complete project documentation and viva defense guide
```

---

## 2. How to Run the Pipeline

Execute from the repository root:

```bash
# 1. Run Preprocessing and generate train/test CSVs
python preprocessing/preprocessing.py

# 2. Train and evaluate the four individual models
python models/linear_regression.py
python models/decision_tree.py
python models/random_forest.py
python models/gradient_boosting.py

# 3. Generate cross-model comparison, plots, and final champion selection
python evaluation/model_comparison.py
```

---

## 3. Measured Experimental Results

All metrics were generated from the actual dataset using **5-Fold Cross-Validation on the training set** (`random_state=42`) and evaluated on the **untouched test set** (802 samples):

| Exp ID | Model | Version | CV R² | CV MAE | CV RMSE | Test R² | Test MAE (log) | Test RMSE (log) | Test MAE (USD $) |
|:---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **EXP_01** | **Linear Regression** | Baseline | 0.6100 | 0.4019 | 0.5271 | 0.5993 | 0.4220 | 0.5414 | $19,667.17 |
| **EXP_02** | **Decision Tree** | Baseline (Unpruned) | 0.3631 | 0.5124 | 0.6736 | 0.3929 | 0.5053 | 0.6663 | $25,724.18 |
| **EXP_03** | **Decision Tree** | Tuned (`max_depth=6`) | 0.6303 | 0.3942 | 0.5129 | 0.6299 | 0.4083 | 0.5203 | $18,410.47 |
| **EXP_04** | **Random Forest** | Baseline (100 trees) | 0.6145 | 0.4017 | 0.5238 | 0.6272 | 0.4093 | 0.5222 | $18,499.99 |
| **EXP_05** | **Random Forest** | Tuned (`max_depth=18, sqrt`) | **0.6638** | **0.3761** | **0.4893** | **0.6595** | **0.3920** | **0.4990** | **$17,733.18** |
| **EXP_06** | **Random Forest** | Selected Feats (4 feats) | 0.6321 | 0.3960 | 0.5118 | 0.6352 | 0.4080 | 0.5166 | $18,542.70 |
| **EXP_07** | **Gradient Boosting** | Baseline (100 trees, lr=0.1) | 0.6650 | 0.3752 | 0.4881 | **0.6619** | 0.3924 | 0.4973 | $18,291.22 |
| **EXP_08** | **Gradient Boosting** | Tuned (150 trees, lr=0.05) | 0.6685 | 0.3745 | 0.4856 | 0.6613 | 0.3928 | 0.4977 | $18,286.72 |

---

## 4. Final Model Selection

- **Champion Ensemble:** **Gradient Boosting Regressor (Baseline)** and **Tuned Random Forest** deliver the best generalization across the board:
  - Highest Test R²: **0.6619** (GBR) / **0.6595** (Tuned RF).
  - Lowest Dollar MAE: **$17,733.18** (Tuned RF).
- **Overfitting Control:** Decision Tree tuning proved the value of pruning (`max_depth=6`), jumping from Test R² 0.3929 to 0.6299.
- **Feature Selection Finding:** Restricting models to the top 4 features degraded R² by ~2.4% to 3.1%, confirming that secondary categorical signals (accidents, fuel type, transmission) contribute meaningful non-linear predictive signal.

---

## 5. Viva Preparation & Defense Highlights

1. **Why `log_price`?** The raw car price is heavily right-skewed (skewness 12.94), dominated by extreme luxury vehicles. Log1p transformation stabilizes variance and brings skewness down to 0.07 (near-normal), optimizing linear and tree MSE loss functions.
2. **Why 5-fold CV?** Evaluates out-of-fold generalization stability and prevents tuning hyperparameters to fit a single split.
3. **How was data leakage prevented?** Continuous feature standardization parameters (\(\mu, \sigma\)) were computed strictly on `X_train` and applied forward to `X_test`. All tuning, cross-validation, and feature ranking operated exclusively on training data.
