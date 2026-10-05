"""
Data Preprocessing Pipeline for Used Car Price Prediction System
Course: IT3051 Fundamentals of Data Mining & Machine Learning

This module performs:
1. Raw dataset loading and symbol cleaning (price, milage)
2. Domain-guided missing value treatment (zero data loss)
3. Duplicate removal and erroneous outlier filtering
4. Fuel type standardization with whitelist
5. Target creation: log_price = log1p(price)
6. Feature engineering: car_age, mileage_per_year, is_luxury_brand, is_manual, is_clean_title, has_accident
7. Fuel type dummy encoding (drop_first=True)
8. Deterministic 80/20 train/test split (random_state=42)
9. Leakage-free standardization on continuous features (fitted strictly on train)
10. Artifact saving for inference and pipeline reproducibility
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

# Global constants for preprocessing consistency
LUXURY_BRANDS = [
    'Porsche', 'Bugatti', 'Ferrari', 'Lamborghini', 'Rolls-Royce', 'Bentley',
    'McLaren', 'Maserati', 'Aston Martin', 'BMW', 'Mercedes-Benz', 'Audi',
    'Lexus', 'Jaguar', 'Cadillac', 'Lincoln', 'Genesis', 'INFINITI',
    'Tesla', 'Land Rover', 'Alfa Romeo', 'Volvo'
]

VALID_FUEL_TYPES = [
    'Gasoline', 'Hybrid', 'Electric', 'E85 Flex Fuel', 'Diesel', 'Plug-In Hybrid', 'Other'
]

FEATURE_COLUMNS = [
    'car_age', 'milage', 'mileage_per_year',
    'is_luxury_brand', 'is_manual', 'is_clean_title', 'has_accident',
    'fuel_E85 Flex Fuel', 'fuel_Electric', 'fuel_Gasoline', 'fuel_Hybrid',
    'fuel_Other', 'fuel_Plug-In Hybrid'
]

CONTINUOUS_COLUMNS = ['car_age', 'milage', 'mileage_per_year']


class CarDataPreprocessor:
    """Preprocessor class encapsulating fitted scaling statistics and feature extraction logic."""

    def __init__(self, means=None, stds=None):
        self.means = means
        self.stds = stds
        self.luxury_brands = LUXURY_BRANDS
        self.valid_fuel_types = VALID_FUEL_TYPES
        self.feature_columns = FEATURE_COLUMNS
        self.continuous_columns = CONTINUOUS_COLUMNS

    def fit(self, X_train_raw):
        """Fit means and stds on training data continuous features."""
        self.means = X_train_raw[self.continuous_columns].mean().to_dict()
        self.stds = X_train_raw[self.continuous_columns].std().to_dict()
        return self

    def transform_single(self, input_dict):
        """
        Transform a single raw user input dictionary into the 13-feature model input DataFrame.
        Expected input_dict keys:
            - model_year (int/float)
            - milage (float)
            - brand (str)
            - transmission (str)
            - clean_title (str: 'Yes' / 'No')
            - accident (str: 'None reported' / 'At least 1 accident or damage reported')
            - fuel_type (str)
        """
        model_year = float(input_dict.get('model_year', 2018))
        milage = float(input_dict.get('milage', 50000.0))
        brand = str(input_dict.get('brand', '')).strip()
        transmission = str(input_dict.get('transmission', 'Automatic')).strip()
        clean_title = str(input_dict.get('clean_title', 'Yes')).strip()
        accident = str(input_dict.get('accident', 'None reported')).strip()
        fuel_type = str(input_dict.get('fuel_type', 'Gasoline')).strip()

        # 1. Feature engineering
        car_age = 2026.0 - model_year
        effective_age = car_age if car_age != 0 else 1.0
        mileage_per_year = milage / effective_age

        is_luxury_brand = 1 if brand in self.luxury_brands else 0
        is_manual = 1 if any(t in transmission.lower() for t in ['m/t', 'manual']) else 0
        is_clean_title = 1 if clean_title.lower() == 'yes' else 0
        has_accident = 1 if 'accident' in accident.lower() or 'damage' in accident.lower() else 0

        # Whitelist fuel type
        if fuel_type not in self.valid_fuel_types:
            fuel_type = 'Other'

        # Continuous scaling
        mu = self.means
        sigma = self.stds
        car_age_scaled = (car_age - mu['car_age']) / sigma['car_age']
        milage_scaled = (milage - mu['milage']) / sigma['milage']
        mpy_scaled = (mileage_per_year - mu['mileage_per_year']) / sigma['mileage_per_year']

        # Construct row matching FEATURE_COLUMNS exactly
        row = {
            'car_age': car_age_scaled,
            'milage': milage_scaled,
            'mileage_per_year': mpy_scaled,
            'is_luxury_brand': is_luxury_brand,
            'is_manual': is_manual,
            'is_clean_title': is_clean_title,
            'has_accident': has_accident,
            'fuel_E85 Flex Fuel': 1 if fuel_type == 'E85 Flex Fuel' else 0,
            'fuel_Electric': 1 if fuel_type == 'Electric' else 0,
            'fuel_Gasoline': 1 if fuel_type == 'Gasoline' else 0,
            'fuel_Hybrid': 1 if fuel_type == 'Hybrid' else 0,
            'fuel_Other': 1 if fuel_type == 'Other' else 0,
            'fuel_Plug-In Hybrid': 1 if fuel_type == 'Plug-In Hybrid' else 0,
        }

        return pd.DataFrame([row])[self.feature_columns]


def run_pipeline(raw_csv_path='used_cars.csv', output_dir='data/processed'):
    """Full preprocessing and dataset generation pipeline."""
    print("=" * 60)
    print("STAGE 4: PREPROCESSING & FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    if not os.path.exists(raw_csv_path):
        alt_path = os.path.join('data', 'raw', 'used_cars.csv')
        if os.path.exists(alt_path):
            raw_csv_path = alt_path
        else:
            raise FileNotFoundError(f"Raw dataset not found at {raw_csv_path} or {alt_path}")

    print(f"Loading raw dataset: {raw_csv_path}")
    df = pd.read_csv(raw_csv_path)
    print(f"Initial raw shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Step 1: Clean price and milage
    df['price'] = df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)
    df['milage'] = df['milage'].astype(str).str.replace(' mi.', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # Step 2: Domain-guided missing value treatment
    df_clean = df.copy()
    df_clean['clean_title'] = df_clean['clean_title'].fillna('No')
    df_clean['accident'] = df_clean['accident'].fillna('None reported')
    is_electric = df_clean['engine'].astype(str).str.contains('Electric', case=False, na=False)
    df_clean.loc[df_clean['fuel_type'].isnull() & is_electric, 'fuel_type'] = 'Electric'
    df_clean['fuel_type'] = df_clean['fuel_type'].fillna('Gasoline')

    # Step 3: Remove duplicate rows
    initial_len = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    dups_removed = initial_len - len(df_clean)
    print(f"Duplicates removed: {dups_removed} (Remaining: {len(df_clean)})")

    # Step 4: Outlier & Typo correction (2005 Maserati typo > $1,000,000)
    typo_mask = (df_clean['brand'] == 'Maserati') & (df_clean['model_year'] == 2005) & (df_clean['price'] > 1_000_000)
    typos_removed = typo_mask.sum()
    df_clean = df_clean[~typo_mask].copy()
    print(f"Erroneous outliers removed: {typos_removed} (Remaining: {len(df_clean)})")

    # Step 5: Whitelist fuel types
    df_clean['fuel_type'] = df_clean['fuel_type'].apply(lambda x: x if x in VALID_FUEL_TYPES else 'Other')

    # Step 6: Target variable log-transformation
    df_clean['log_price'] = np.log1p(df_clean['price'])

    # Step 7: Feature Engineering
    df_clean['is_clean_title'] = (df_clean['clean_title'] == 'Yes').astype(int)
    df_clean['has_accident'] = (df_clean['accident'] == 'At least 1 accident or damage reported').astype(int)
    df_clean['is_manual'] = df_clean['transmission'].astype(str).str.contains('M/T|Manual', case=False, na=False).astype(int)
    df_clean['is_luxury_brand'] = df_clean['brand'].isin(LUXURY_BRANDS).astype(int)
    df_clean['car_age'] = 2026 - df_clean['model_year']
    df_clean['mileage_per_year'] = df_clean['milage'] / df_clean['car_age'].replace(0, 1)

    # Dummy variables for fuel_type (drop_first=True to avoid multicollinearity)
    fuel_dummies = pd.get_dummies(df_clean['fuel_type'], prefix='fuel', drop_first=True, dtype=int)
    df_final = pd.concat([df_clean, fuel_dummies], axis=1)

    X = df_final[FEATURE_COLUMNS].copy()
    y = df_final['log_price'].copy()

    # Step 8: Deterministic 80/20 train/test split
    np.random.seed(42)
    idx = np.random.permutation(len(X))
    split = int(0.8 * len(X))

    X_train = X.iloc[idx[:split]].copy()
    X_test = X.iloc[idx[split:]].copy()
    y_train = y.iloc[idx[:split]].copy()
    y_test = y.iloc[idx[split:]].copy()

    # Step 9: Leakage-free standardization on continuous features
    preprocessor = CarDataPreprocessor()
    preprocessor.fit(X_train)

    for col in CONTINUOUS_COLUMNS:
        X_train[col] = (X_train[col] - preprocessor.means[col]) / preprocessor.stds[col]
        X_test[col] = (X_test[col] - preprocessor.means[col]) / preprocessor.stds[col]

    print("\nLeakage Prevention Verification:")
    for col in CONTINUOUS_COLUMNS:
        print(f"  Train {col:<18} -> Mean: {X_train[col].mean():.6f}, Std: {X_train[col].std():.6f}")
        print(f"  Test  {col:<18} -> Mean: {X_test[col].mean():.6f}, Std: {X_test[col].std():.6f}")

    # Step 10: Save datasets
    os.makedirs(output_dir, exist_ok=True)
    X_train_path = os.path.join(output_dir, 'X_train.csv')
    X_test_path = os.path.join(output_dir, 'X_test.csv')
    y_train_path = os.path.join(output_dir, 'y_train.csv')
    y_test_path = os.path.join(output_dir, 'y_test.csv')

    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    # Also keep synced at root for notebook convenience
    X_train.to_csv('X_train.csv', index=False)
    X_test.to_csv('X_test.csv', index=False)
    y_train.to_csv('y_train.csv', index=False)
    y_test.to_csv('y_test.csv', index=False)

    # Save artifacts
    os.makedirs('artifacts/preprocessing', exist_ok=True)
    preprocessor_joblib_path = os.path.join('artifacts', 'preprocessing', 'preprocessor.joblib')
    preprocessor_state = {
        'means': preprocessor.means,
        'stds': preprocessor.stds,
        'luxury_brands': LUXURY_BRANDS,
        'valid_fuel_types': VALID_FUEL_TYPES,
        'feature_columns': FEATURE_COLUMNS,
        'continuous_columns': CONTINUOUS_COLUMNS
    }
    joblib.dump(preprocessor_state, preprocessor_joblib_path)

    metadata = {
        'num_samples_total': int(len(X)),
        'num_train_samples': int(len(X_train)),
        'num_test_samples': int(len(X_test)),
        'target_variable': 'log_price',
        'target_formula': 'log1p(price)',
        'target_inverse_formula': 'expm1(log_price)',
        'feature_count': int(len(FEATURE_COLUMNS)),
        'feature_names': FEATURE_COLUMNS,
        'continuous_features': CONTINUOUS_COLUMNS,
        'train_means': preprocessor.means,
        'train_stds': preprocessor.stds,
        'luxury_brands': LUXURY_BRANDS,
        'valid_fuel_types': VALID_FUEL_TYPES
    }

    metadata_path = os.path.join('artifacts', 'preprocessing', 'preprocessing_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    os.makedirs('artifacts/metadata', exist_ok=True)
    with open(os.path.join('artifacts', 'metadata', 'feature_names.json'), 'w') as f:
        json.dump({'features': FEATURE_COLUMNS}, f, indent=2)

    print(f"\n[OK] Preprocessing completed successfully.")
    print(f"  Processed data: {output_dir}/")
    print(f"  Fitted preprocessor: {preprocessor_joblib_path}")
    print(f"  Metadata: {metadata_path}")

    return X_train, X_test, y_train, y_test, preprocessor


if __name__ == '__main__':
    run_pipeline()
