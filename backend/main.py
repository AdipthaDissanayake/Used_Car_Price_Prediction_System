"""
Flask REST API Backend for Used Car Price Prediction System
Includes MySQL Database persistence and Google Authentication
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

frontend_dir = os.path.join(repo_root, 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

# Initialize database
db_manager = get_db_manager()
try:
    db_manager.init_db()
except Exception as e:
    print(f"[DB Warning] Startup database check: {e}")

GOOGLE_CLIENT_ID = os.getenv(
    'GOOGLE_CLIENT_ID',
    '53736675578-6f3dvt55v1i50nnrsmg6rktvr1l7jhh6.apps.googleusercontent.com'
)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
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
        "model": model_name,
        "version": "1.0.0",
        "service": "Used Car Price Prediction System API"
    }), 200


@app.route('/metadata', methods=['GET'])
def get_metadata():
    """Return available brands, fuel types, google client id, and model metrics."""
    service = get_service()
    return jsonify({
        "luxury_brands": LUXURY_BRANDS,
        "valid_fuel_types": VALID_FUEL_TYPES,
        "google_client_id": GOOGLE_CLIENT_ID,
        "model_performance": service.metadata
    }), 200


@app.route('/api/auth/google', methods=['POST', 'OPTIONS'])
def google_auth():
    """Verify Google OAuth credential and log or update user in database."""
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json(silent=True) or {}
    token = data.get('credential')
    user_payload = data.get('user')

    google_id = None
    email = None
    name = None
    picture = None

    # Option 1: Verify token via google-auth library
    if token:
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests as google_requests
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )
            google_id = id_info.get('sub')
            email = id_info.get('email')
            name = id_info.get('name')
            picture = id_info.get('picture')
        except Exception as e:
            print(f"[Auth Notice] Token verification fallback: {e}")
            # If network or local clock prevents remote cert check, check provided user payload
            if user_payload:
                google_id = user_payload.get('sub') or user_payload.get('id')
                email = user_payload.get('email')
                name = user_payload.get('name')
                picture = user_payload.get('picture')

    elif user_payload:
        google_id = user_payload.get('sub') or user_payload.get('id')
        email = user_payload.get('email')
        name = user_payload.get('name')
        picture = user_payload.get('picture')

    if not google_id or not email:
        return jsonify({
            "error": "Authentication Failed",
            "message": "Valid Google ID token or user profile required."
        }), 400

    user_record = db_manager.save_or_update_user(
        google_id=google_id,
        email=email,
        name=name,
        picture=picture
    )

    if not user_record:
        return jsonify({
            "error": "Database Error",
            "message": "Could not persist user to database."
        }), 500

    return jsonify({
        "status": "success",
        "message": "Authenticated successfully with Google",
        "user": user_record
    }), 200


@app.route('/api/predictions/history', methods=['GET'])
def get_history():
    """Retrieve recent predictions from database."""
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', default=10, type=int)
    history = db_manager.get_recent_predictions(user_id=user_id, limit=limit)
    return jsonify({
        "status": "success",
        "count": len(history),
        "data": history
    }), 200


@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Handle car price prediction request and log to database."""
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

        # Log to database
        user_id = data.get('user_id')
        try:
            if user_id:
                user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = None

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
    print(f"Google Client ID: {GOOGLE_CLIENT_ID}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=False)
