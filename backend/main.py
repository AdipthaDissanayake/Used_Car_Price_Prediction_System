"""
Flask REST API Backend for Used Car Price Prediction System
Includes MySQL Database persistence, User Authentication (Register/Login via JWT),
User-specific Prediction History, and History Deletion capabilities.
Stage 9: Backend Development - IT3051
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

# Load environment variables
load_dotenv()

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.schemas import validate_car_payload, ValidationError
from backend.service import get_service, LUXURY_BRANDS, VALID_FUEL_TYPES
from backend.database import get_db_manager
from backend.auth import create_access_token, verify_access_token

frontend_dir = os.path.join(repo_root, 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

# Initialize database
db_manager = get_db_manager()
try:
    db_manager.init_db()
except Exception as e:
    print(f"[DB Warning] Startup database check: {e}")


def get_current_user_from_request():
    """Extract and verify user from Authorization Bearer token header."""
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1].strip()
        decoded = verify_access_token(token)
        if decoded:
            return decoded
    return None


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,OPTIONS'
    return response


@app.route('/', methods=['GET'])
def serve_index():
    """Serve the frontend user interface."""
    if os.path.exists(os.path.join(frontend_dir, 'index.html')):
        return send_from_directory(frontend_dir, 'index.html')
    return jsonify({
        "message": "Used Car Price Prediction API is operational. Visit /health or POST /predict."
    })


@app.route('/health', methods=['GET'])
def health_check():
    """System health check endpoint."""
    try:
        service = get_service()
        model_name = service.metadata.get('champion_model', 'Gradient Boosting Regressor')
        status = "healthy"
    except Exception as e:
        status = f"unhealthy: {str(e)}"
        model_name = "unavailable"

    db_type = "MySQL" if db_manager.is_mysql else "SQLite"

    return jsonify({
        "status": status,
        "database": db_type,
        "database_connected": True,
        "auth_system": "JWT",
        "model": model_name,
        "version": "2.0.0",
        "service": "Used Car Price Prediction System API"
    }), 200


@app.route('/metadata', methods=['GET'])
def get_metadata():
    """Return available brands, fuel types, and champion model metrics."""
    service = get_service()
    return jsonify({
        "luxury_brands": LUXURY_BRANDS,
        "valid_fuel_types": VALID_FUEL_TYPES,
        "model_performance": service.metadata
    }), 200


# =========================================================================
# User Authentication Endpoints (Register / Login / Profile)
# =========================================================================

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user account with email and password."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()

    if not email or '@' not in email or '.' not in email:
        return jsonify({"error": "Validation Error", "message": "A valid email address is required."}), 400

    if not password or len(password) < 6:
        return jsonify({"error": "Validation Error", "message": "Password must be at least 6 characters long."}), 400

    user_record, err = db_manager.register_user(email=email, password=password, name=name)
    if err:
        return jsonify({"error": "Registration Error", "message": err}), 400

    token = create_access_token(user_record)
    return jsonify({
        "status": "success",
        "message": "Account created successfully.",
        "token": token,
        "user": user_record
    }), 201


@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate user with email and password."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"error": "Validation Error", "message": "Email and password are required."}), 400

    user_record, err = db_manager.authenticate_user(email=email, password=password)
    if err or not user_record:
        return jsonify({"error": "Unauthorized", "message": err or "Invalid email or password."}), 401

    token = create_access_token(user_record)
    return jsonify({
        "status": "success",
        "message": "Signed in successfully.",
        "token": token,
        "user": user_record
    }), 200


@app.route('/api/auth/me', methods=['GET'])
def get_me():
    """Return profile of currently authenticated user."""
    user = get_current_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Valid authentication token required."}), 401
    return jsonify({"status": "success", "user": user}), 200


# =========================================================================
# Prediction & User-Specific History Endpoints (Query & Deletion)
# =========================================================================

@app.route('/api/predictions/history', methods=['GET'])
def get_history():
    """Retrieve valuation history strictly for the authenticated user."""
    user = get_current_user_from_request()
    if not user:
        return jsonify({"status": "success", "count": 0, "data": []}), 200

    limit = request.args.get('limit', default=20, type=int)
    history = db_manager.get_user_predictions(user_id=int(user['id']), limit=limit)
    return jsonify({
        "status": "success",
        "count": len(history),
        "data": history
    }), 200


@app.route('/api/predictions/history/<int:log_id>', methods=['DELETE', 'OPTIONS'])
def delete_single_history(log_id):
    """Delete an individual valuation history item owned by current user."""
    if request.method == 'OPTIONS':
        return '', 204

    user = get_current_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Sign in required to delete history."}), 401

    deleted = db_manager.delete_prediction_log(log_id=log_id, user_id=int(user['id']))
    if not deleted:
        return jsonify({"error": "Not Found", "message": "Record not found or not owned by user."}), 404

    return jsonify({"status": "success", "message": f"Prediction #{log_id} deleted successfully."}), 200


@app.route('/api/predictions/history', methods=['DELETE', 'OPTIONS'])
def clear_all_history():
    """Clear all valuation history for the authenticated user."""
    if request.method == 'OPTIONS':
        return '', 204

    user = get_current_user_from_request()
    if not user:
        return jsonify({"error": "Unauthorized", "message": "Sign in required to clear history."}), 401

    count = db_manager.clear_user_predictions(user_id=int(user['id']))
    return jsonify({
        "status": "success",
        "message": f"Cleared {count} valuation records from your history.",
        "deleted_count": count
    }), 200


@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Handle vehicle valuation request and log to user account if authenticated."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            "error": "Bad Request",
            "message": "Malformed or missing JSON body in request."
        }), 400

    try:
        cleaned_payload, _ = validate_car_payload(data)
    except ValidationError as ve:
        return jsonify({
            "error": "Validation Error",
            "message": ve.message
        }), ve.status_code
    except Exception as e:
        return jsonify({
            "error": "Bad Request",
            "message": str(e)
        }), 400

    try:
        service = get_service()
        result = service.predict(cleaned_payload)

        # Attach to authenticated user if signed in
        token_user = get_current_user_from_request()
        if token_user and token_user.get('id'):
            user_id = int(token_user.get('id'))
            db_log = db_manager.log_prediction(
                payload=cleaned_payload,
                predicted_price=result['predicted_price'],
                log_price=result['log_price'],
                user_id=user_id
            )
            if db_log:
                result['log_id'] = db_log.get('id')

        return jsonify({
            "status": "success",
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "error": "Internal Prediction Error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print(f"Used Car Price Prediction Backend starting on http://localhost:{port}")
    print(f"Database: {os.getenv('DATABASE_URL')}")
    print("Authentication: Email/Password JWT")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
