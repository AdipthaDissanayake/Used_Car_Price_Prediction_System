# Used Car Price Prediction System
## IT3051 – Fundamentals of Data Mining & Machine Learning (Mini Project 2026)

End-to-end Machine Learning System predicting used car market selling prices from vehicle characteristics.

- **Target Variable**: `log_price` (log-transformed selling price using $\log(1 + \text{price})$ to stabilize right-skewed car distributions).
- **Inversion Formula**: $\text{Price} = \exp(\text{log\_price}) - 1$.
- **Core Algorithms**: Linear Regression, Decision Tree Regressor, Random Forest Regressor, and Gradient Boosting Regressor.

---

## 1. Project Architecture & Directory Structure

```text
Used_Car_Price_Prediction_System/
│
├── data/
│   ├── raw/
│   │   └── used_cars.csv                    # Original raw dataset (4,009 rows x 12 cols)
│   └── processed/
│       ├── X_train.csv                     # Standardized training features (3,206 rows x 13 cols)
│       ├── X_test.csv                      # Standardized testing features (802 rows x 13 cols)
│       ├── y_train.csv                     # Training log target (3,206 rows)
│       └── y_test.csv                      # Testing log target (802 rows)
│
├── preprocessing/
│   └── preprocessing.py                    # Preprocessing pipeline, leakage-free scaling & exports
│
├── models/
│   ├── linear_regression.py                # Model 1: Linear Regression (OLS baseline)
│   ├── decision_tree.py                    # Model 2: Decision Tree Regressor (baseline & tuned)
│   ├── random_forest.py                    # Model 3: Random Forest Regressor (baseline & tuned)
│   └── gradient_boosting.py                # Model 4: Gradient Boosting Regressor (baseline & tuned)
│
├── tuning/
│   └── tuning.py                           # Cross-validation hyperparameter tuning experiments
│
├── evaluation/
│   └── model_comparison.py                 # Multi-model evaluation, plot generation, champion export
│
├── artifacts/
│   ├── models/
│   │   ├── final_model.joblib              # Champion serialized model (Gradient Boosting)
│   │   ├── linear_regression.joblib
│   │   ├── decision_tree.joblib
│   │   ├── random_forest.joblib
│   │   └── gradient_boosting.joblib
│   ├── preprocessing/
│   │   ├── preprocessor.joblib             # Fitted feature scaler & state dictionary
│   │   └── preprocessing_metadata.json     # Feature names, means, stds, whitelists
│   └── metadata/
│       ├── feature_names.json              # Ordered list of 13 input features
│       └── model_registry.json             # Model metadata & status registry
│
├── results/
│   ├── baseline_results.csv                # Baseline performance comparison table
│   ├── tuned_results.csv                   # Tuned performance comparison table
│   ├── experiment_log.csv                  # Full log of all experimental iterations
│   ├── final_model_results.json            # Final metrics JSON for report generation
│   ├── system_test_results.csv             # Automated test execution evidence (20/20 PASSED)
│   ├── feature_importance/
│   │   ├── rf_feature_importance.csv
│   │   ├── gb_feature_importance.csv
│   │   └── dt_feature_importance.csv
│   └── plots/
│       ├── model_r2_comparison.png
│       ├── final_model_pred_vs_actual.png
│       └── final_model_residual_distribution.png
│
├── backend/
│   ├── main.py                             # Flask REST API server & static frontend host
│   ├── schemas.py                          # Request payload validation & boundary checking
│   └── service.py                          # Model inference service with confidence intervals
│
├── frontend/
│   ├── index.html                          # Interactive vehicle valuation web interface
│   ├── style.css                           # Modern responsive stylesheet
│   └── app.js                              # Client validation, API requests, and live results
│
├── tests/
│   ├── test_preprocessing.py               # Preprocessing, shapes, and leakage prevention tests
│   ├── test_models.py                      # Model inference and artifact validation tests
│   ├── test_backend.py                     # API endpoint, status codes, and validation tests
│   └── test_end_to_end.py                  # Integration tests & real-world pricing logic tests
│
└── README.md                               # Project documentation & execution guide
```

---

## 2. Environment Setup & Configuration

### Dependencies
Ensure Python 3.10+ (tested on Python 3.14 on Windows):
```bash
pip install scikit-learn pandas numpy matplotlib seaborn flask pytest joblib pymysql python-dotenv google-auth
```

### Environment Variables (`.env`)
The system loads configurations automatically from `.env`:
```ini
DATABASE_URL=mysql+pymysql://finassist_app:root@localhost:3306/used_car_price_db
GOOGLE_CLIENT_ID=53736675578-6f3dvt55v1i50nnrsmg6rktvr1l7jhh6.apps.googleusercontent.com
SECRET_KEY=used_car_price_prediction_secret_key_2026
PORT=5000
```
- **Database**: Connects to MySQL (`used_car_price_db`) with automatic table creation (`users` and `prediction_logs`). If MySQL is offline, it gracefully falls back to local SQLite so the system never crashes.
- **Authentication**: Integrates Google Identity Services for one-tap and pop-up sign-in. Authenticated user sessions are stored in the database alongside their vehicle prediction history.

---

## 3. How to Run the Pipeline

Execute all commands from the repository root:

### Step 1: Preprocessing & Data Generation
```bash
py preprocessing/preprocessing.py
```
- Fits continuous scalers (`car_age`, `milage`, `mileage_per_year`) strictly on the training set.
- Exports `data/processed/X_train.csv`, `X_test.csv`, `y_train.csv`, `y_test.csv`.
- Serializes `artifacts/preprocessing/preprocessor.joblib`.

### Step 2: Model Training & Evaluation
```bash
py models/linear_regression.py
py models/decision_tree.py
py models/random_forest.py
py models/gradient_boosting.py
```

### Step 3: Hyperparameter Tuning & Model Selection
```bash
py tuning/tuning.py
py evaluation/model_comparison.py
```
- Executes 5-fold cross-validation on training data.
- Exports evaluation plots to `results/plots/`.
- Saves champion model to `artifacts/models/final_model.joblib`.

### Step 4: Run the Backend & Frontend Web Application
```bash
py backend/main.py
```
Open your browser and navigate to:
**http://localhost:5000**

Features:
- Complete vehicle evaluation UI.
- Real-time client-side validation.
- Live API integration (`POST /predict`).
- Valuation summary with 90% confidence interval, model specs, and interpretability insights.

### Step 5: Run Automated Test Suite
```bash
py -m pytest tests/ -v
```
All 20 test cases pass with 100% test coverage across:
- `test_preprocessing.py`: data split dimensions, null checks, leakage checks, single transform.
- `test_models.py`: artifact loading, prediction validity, $R^2$ thresholds.
- `test_backend.py`: `/health`, `/metadata`, valid predictions, invalid year/mileage (422), missing fields (400).
- `test_end_to_end.py`: luxury vs economy valuation, mileage depreciation, accident history penalty.

---

## 4. Empirical Evaluation Results

All metrics were computed strictly using **5-Fold Cross-Validation on the training set** (`random_state=42`) and evaluated on the **untouched test set** (802 samples):

| Model | Variant | CV $R^2$ (Mean $\pm$ Std) | CV MAE (log) | CV RMSE (log) | Test $R^2$ | Test MAE (log) | Test RMSE (log) | Test MAE (USD $) | Test RMSE (USD $) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Linear Regression** | Baseline | $0.6100 \pm 0.0141$ | 0.4019 | 0.5271 | 0.5993 | 0.4220 | 0.5414 | $19,667.17 | $44,886.72 |
| **Decision Tree** | Baseline (Default) | $0.3631 \pm 0.0202$ | 0.5124 | 0.6736 | 0.3929 | 0.5053 | 0.6663 | $25,724.18 | $79,266.97 |
| **Decision Tree** | Tuned (`depth=6, leaf=15`) | $0.6303 \pm 0.0180$ | 0.3942 | 0.5129 | 0.6299 | 0.4083 | 0.5203 | $18,410.47 | $37,918.03 |
| **Random Forest** | Baseline ($n=100$) | $0.6145 \pm 0.0192$ | 0.4017 | 0.5238 | 0.6272 | 0.4093 | 0.5222 | $18,499.99 | $39,184.06 |
| **Random Forest** | Tuned (`depth=18, sqrt, leaf=4`) | **$0.6638 \pm 0.0118$** | **0.3761** | **0.4893** | **0.6595** | **0.3920** | **0.4990** | **$17,733.18** | $38,630.60 |
| **Gradient Boosting** | Baseline ($n=100, \text{lr}=0.1$) | **$0.6650 \pm 0.0211$** | **0.3752** | **0.4881** | **0.6619** | **0.3924** | **0.4973** | $18,291.22 | **$39,318.53** |
| **Gradient Boosting** | Tuned ($n=150, \text{lr}=0.05$) | **$0.6668 \pm 0.0181$** | 0.3745 | 0.4856 | **0.6645** | 0.3914 | 0.4977 | $18,199.59 | $39,350.88 |

---

## 5. Key Empirical Findings

1. **Champion Model Selection**:
   - **Gradient Boosting Regressor** is selected as the primary production model, delivering the highest Test $R^2$ (**0.6619** baseline / **0.6645** tuned) and lowest Test RMSE (**0.4973** log).
   - **Tuned Random Forest Regressor** is the top runner-up, achieving the lowest absolute dollar error (**Test MAE: $17,733.18**).
2. **Decision Tree Regularization**:
   - Unconstrained Decision Tree severely overfits (CV $R^2 = 0.3631$, Test $R^2 = 0.3929$).
   - Pruning (`max_depth=6`, `min_samples_leaf=15`) improved Test $R^2$ by **+0.2370** to **0.6299**, reducing Test MAE by over **$7,300**.
3. **Feature Importance Hierarchy**:
   - `milage` and `car_age` are the dominant primary drivers of car value (~70–80% cumulative importance).
   - `is_luxury_brand` is the strongest categorical predictor (~5–6% importance).
   - Title condition, accident status, and fuel type provide non-linear corrections that boost overall ensemble accuracy.

---

## 6. REST API Documentation

### `GET /health`
Returns system status and loaded model information.
```json
{
  "status": "healthy",
  "model": "Gradient Boosting Regressor",
  "version": "1.0.0",
  "service": "Used Car Price Prediction System API"
}
```

### `POST /predict`
Estimates vehicle selling price from specifications.

**Request Payload:**
```json
{
  "brand": "Porsche",
  "model_year": 2021,
  "milage": 18000,
  "transmission": "Automatic",
  "clean_title": "Yes",
  "accident": "None reported",
  "fuel_type": "Gasoline"
}
```

**Response (HTTP 200):**
```json
{
  "status": "success",
  "data": {
    "predicted_price": 69247.85,
    "predicted_price_formatted": "$69,247.85",
    "price_range_90_pct": {
      "lower": 30557.77,
      "upper": 156922.93,
      "formatted": "$30,557.77 - $156,922.93"
    },
    "log_price": 11.1455,
    "model_used": "Gradient Boosting Regressor",
    "model_test_r2": 0.6619,
    "insights": [
      "Luxury tier vehicle: Higher value retention and prestige premium applied.",
      "Clean history (no accident reported): High value retention."
    ]
  }
}
```

---

## 7. Artifacts Inventory for Technical Report Writer (Stage 11)

For the group member preparing the Stage 11 Technical Report, all evidence and figures are ready to cite:
- **Baseline Metrics**: `results/baseline_results.csv`
- **Tuned Metrics**: `results/tuned_results.csv`
- **Full Experiment History**: `results/experiment_log.csv`
- **Final Model Results**: `results/final_model_results.json`
- **Test Suite Verification Evidence**: `results/system_test_results.csv` (20 automated tests passed)
- **Feature Importance Rankings**: `results/feature_importance/` (`rf_feature_importance.csv`, `gb_feature_importance.csv`, `dt_feature_importance.csv`)
- **Visual Plots (High Resolution PNG)**:
  - `results/plots/model_r2_comparison.png`
  - `results/plots/final_model_pred_vs_actual.png`
  - `results/plots/final_model_residual_distribution.png`
