# src/api/authentications/auth_utils.py
import jwt
from functools import wraps
from flask import request, g
from src.config.constants import JWT_SECRET_KEY
import logging

logger = logging.getLogger(__name__)

def token_required(func):
    """
    Decorator to protect Flask-RESTful methods with JWT authentication.
    Returns (dict, status) on auth errors so flask-restful can serialize it.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            return {"error": "Authorization Token missing"}, 401

        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return {"error": "Invalid authorization Token format"}, 401

        token = parts[1]

        try:
            # Decode and verify the JWT
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            g.user_email = payload.get("sub")  # store user info in Flask global context
            g.jwt_payload = payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}, 401
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return {"error": "Token validation error"}, 401

        # Proceed to actual route function
        return func(*args, **kwargs)
    return wrapper
