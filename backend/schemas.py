"""
Data Validation Schemas for Used Car Price Prediction Backend
"""

from typing import Dict, Any, Tuple, Optional


VALID_CLEAN_TITLE = {'yes', 'no'}
VALID_ACCIDENTS = {
    'none reported',
    'none',
    'at least 1 accident or damage reported',
    'at least 1 accident',
    'yes',
    'no'
}

VALID_FUEL_TYPES = [
    'Gasoline', 'Hybrid', 'Electric', 'E85 Flex Fuel', 'Diesel', 'Plug-In Hybrid', 'Other'
]


class ValidationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_car_payload(data: Any) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Validate and sanitize input payload for car price prediction.
    Returns (cleaned_dict, error_message).
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a valid JSON object.", 400)

    # Required fields check
    required_fields = ['model_year', 'milage', 'brand', 'transmission', 'clean_title', 'accident', 'fuel_type']
    missing = [f for f in required_fields if f not in data or data[f] is None or str(data[f]).strip() == ""]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}", 400)

    # 1. model_year validation
    try:
        model_year = int(data['model_year'])
    except (ValueError, TypeError):
        raise ValidationError("Field 'model_year' must be a valid integer.", 422)

    if model_year < 1900 or model_year > 2026:
        raise ValidationError(f"Field 'model_year' ({model_year}) out of allowable range [1900, 2026].", 422)

    # 2. milage validation
    try:
        milage = float(data['milage'])
    except (ValueError, TypeError):
        raise ValidationError("Field 'milage' must be a numeric value.", 422)

    if milage < 0:
        raise ValidationError(f"Field 'milage' cannot be negative ({milage}).", 422)
    if milage > 1_500_000:
        raise ValidationError(f"Field 'milage' ({milage}) exceeds realistic threshold (1,500,000 miles).", 422)

    # 3. brand validation
    brand = str(data['brand']).strip()
    if not brand:
        raise ValidationError("Field 'brand' cannot be empty.", 400)

    # 4. transmission
    transmission = str(data['transmission']).strip()
    if not transmission:
        raise ValidationError("Field 'transmission' cannot be empty.", 400)

    # 5. clean_title
    clean_title = str(data['clean_title']).strip()
    if clean_title.lower() not in VALID_CLEAN_TITLE:
        raise ValidationError("Field 'clean_title' must be 'Yes' or 'No'.", 422)

    # 6. accident
    accident = str(data['accident']).strip()
    if accident.lower() not in VALID_ACCIDENTS:
        raise ValidationError(
            "Field 'accident' must be 'None reported' or 'At least 1 accident or damage reported'.", 422
        )

    # 7. fuel_type
    fuel_type = str(data['fuel_type']).strip()
    matched_fuel = None
    for vf in VALID_FUEL_TYPES:
        if fuel_type.lower() == vf.lower():
            matched_fuel = vf
            break
    if not matched_fuel:
        matched_fuel = 'Other'

    cleaned = {
        'model_year': model_year,
        'milage': milage,
        'brand': brand,
        'transmission': transmission,
        'clean_title': 'Yes' if clean_title.lower() == 'yes' else 'No',
        'accident': 'At least 1 accident or damage reported' if any(w in accident.lower() for w in ['at least', 'yes', 'damage', 'reported']) and 'none' not in accident.lower() else 'None reported',
        'fuel_type': matched_fuel
    }

    return cleaned, None
