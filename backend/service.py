"""
Inference Service for Used Car Price Prediction Backend
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Add repo root to path for imports
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from preprocessing.preprocessing import CarDataPreprocessor, LUXURY_BRANDS, VALID_FUEL_TYPES


class PredictionService:
    def __init__(self, model_path=None, preprocessor_path=None):
        self.repo_root = repo_root
        self.model_path = model_path or os.path.join(repo_root, 'artifacts', 'models', 'final_model.joblib')
        self.preprocessor_path = preprocessor_path or os.path.join(repo_root, 'artifacts', 'preprocessing', 'preprocessor.joblib')
        self.metadata_path = os.path.join(repo_root, 'results', 'final_model_results.json')

        self.model = None
        self.preprocessor = None
        self.metadata = {}
        self.load_artifacts()

    def load_artifacts(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Champion model not found at {self.model_path}. Please train the models first.")
        self.model = joblib.load(self.model_path)

        # Load preprocessor
        if os.path.exists(self.preprocessor_path):
            loaded = joblib.load(self.preprocessor_path)
            if isinstance(loaded, dict):
                self.preprocessor = CarDataPreprocessor(means=loaded['means'], stds=loaded['stds'])
            elif hasattr(loaded, 'transform_single'):
                self.preprocessor = loaded
            else:
                self.preprocessor = CarDataPreprocessor(means=loaded.get('means'), stds=loaded.get('stds'))
        else:
            # Fallback: instantiate preprocessor and fit using X_train.csv
            train_path = os.path.join(self.repo_root, 'data', 'processed', 'X_train.csv')
            if not os.path.exists(train_path):
                train_path = os.path.join(self.repo_root, 'X_train.csv')
            df_train = pd.read_csv(train_path)
            self.preprocessor = CarDataPreprocessor()
            self.preprocessor.fit(df_train)

        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)

    def predict(self, raw_input: dict) -> dict:
        """
        Generate price prediction and interpretable insights from raw car features.
        """
        # Transform into model input
        X_df = self.preprocessor.transform_single(raw_input)

        # Predict log price
        pred_log_price = float(self.model.predict(X_df)[0])

        # Target inversion via expm1
        pred_price = float(np.expm1(pred_log_price))
        # Ensure realistic lower bound (at least $500)
        pred_price = max(500.0, pred_price)

        # Calculate estimated 90% confidence interval based on test RMSE (0.4973 log)
        test_rmse = float(self.metadata.get('test_rmse_log', 0.4973))
        lower_price = float(np.expm1(pred_log_price - 1.645 * test_rmse))
        upper_price = float(np.expm1(pred_log_price + 1.645 * test_rmse))
        lower_price = max(500.0, lower_price)

        # Interpretability insights
        is_luxury = raw_input.get('brand', '') in LUXURY_BRANDS
        has_accident = 'accident' in raw_input.get('accident', '').lower() or 'damage' in raw_input.get('accident', '').lower()
        car_age = 2026.0 - float(raw_input.get('model_year', 2018))
        milage = float(raw_input.get('milage', 50000.0))

        insights = []
        if is_luxury:
            insights.append("Luxury tier vehicle: Higher value retention and prestige premium applied.")
        else:
            insights.append("Mainstream tier vehicle: Valued under competitive high-volume market dynamics.")

        if has_accident:
            insights.append("Reported accident history: Value adjusted downward due to prior structural or body damage record.")
        else:
            insights.append("Clean history (no accident reported): High value retention.")

        if car_age <= 3:
            insights.append(f"Near-new vehicle ({int(car_age)} years old): Prime depreciation phase.")
        elif car_age > 10:
            insights.append(f"Mature vehicle ({int(car_age)} years old): Depreciated market baseline.")

        return {
            'predicted_price': round(pred_price, 2),
            'predicted_price_formatted': f"${pred_price:,.2f}",
            'price_range_90_pct': {
                'lower': round(lower_price, 2),
                'upper': round(upper_price, 2),
                'formatted': f"${lower_price:,.2f} - ${upper_price:,.2f}"
            },
            'log_price': round(pred_log_price, 4),
            'model_used': self.metadata.get('champion_model', 'Gradient Boosting Regressor'),
            'model_test_r2': self.metadata.get('test_r2', 0.6619),
            'insights': insights,
            'input_summary': {
                'brand': raw_input.get('brand'),
                'model_year': raw_input.get('model_year'),
                'car_age': int(car_age),
                'milage': milage,
                'transmission': raw_input.get('transmission'),
                'clean_title': raw_input.get('clean_title'),
                'accident': raw_input.get('accident'),
                'fuel_type': raw_input.get('fuel_type')
            }
        }


# Global singleton instance
service = None


def get_service() -> PredictionService:
    global service
    if service is None:
        service = PredictionService()
    return service
