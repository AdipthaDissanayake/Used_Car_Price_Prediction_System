"""
JWT Authentication Utility for Used Car Price Prediction System
Uses JWT_SECRET_KEY to generate and verify cryptographically signed tokens.
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import jwt

load_dotenv()

JWT_SECRET_KEY = os.getenv(
    'JWT_SECRET_KEY',
    'eONnP6QykYwhnAw_7Dq612Sj-io9UfwUV1wFXJMNF6QiIMAmFzmfLHOHsXBQgZ8FramcE5DQoBI6LiHFIczorw'
)
ALGORITHM = "HS256"


def create_access_token(user_data: dict, expires_delta: timedelta = None) -> str:
    """Generate a signed JWT token containing user identity and expiration."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

    payload = {
        "sub": str(user_data.get("id")),
        "id": user_data.get("id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_access_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
