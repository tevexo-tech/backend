import hashlib
import jwt
import datetime
import uuid
import logging
from flask import request
from flask_restful import Resource
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_connection import byte_master_connection
from src.config.constants import JWT_SECRET_KEY
import re

logger = logging.getLogger(__name__)

def md5_hash_password(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()
def is_strong_password(password: str) -> bool:
    """
    Validate password strength.
    - At least 8 characters
    - Contains uppercase, lowercase, number, and special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

class SignupAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or not data.get("username") or not data.get("email") or not data.get("password"):
                return {"message": "Username, email, and password are required"}, 400

            username = data["username"]
            email = data["email"]
            password = data["password"]

            # ✅ Password strength check
            if not is_strong_password(password):
                return {
                    "message": (
                        "Password must be at least 8 characters long, "
                        "and include an uppercase letter, lowercase letter, "
                        "a number, and a special character."
                    )
                }, 400

            with byte_master_connection() as session:
                existing_user = session.execute(
                    text("SELECT * FROM candidates WHERE username = :username OR email = :email"),
                    {"username": username, "email": email}
                ).fetchone()

                if existing_user:
                    return {"message": "Username or email already exists"}, 400

                hashed_password = md5_hash_password(password)
                candidate_id = str(uuid.uuid4())

                session.execute(
                    text("""
                        INSERT INTO candidates (username, email, password, candidate_id, created_at, updated_at)
                        VALUES (:username, :email, :password, :candidate_id, :created_at, :updated_at)
                    """),
                    {
                        "username": username,
                        "email": email,
                        "password": hashed_password,
                        "candidate_id": candidate_id,
                        "created_at": datetime.datetime.now(),
                        "updated_at": datetime.datetime.now()
                    }
                )
                session.commit()

            return {
                "message": "User created successfully",
                "user": {"username": username, "email": email, "candidate_id": candidate_id}
            }, 201

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return {"message": "Database error occurred"}, 500

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"message": "Unexpected error occurred"}, 500



class LoginAPI(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or not data.get("email") or not data.get("password"):
                return {"message": "Email and password are required"}, 400

            email = data["email"]
            password = data["password"]

            with byte_master_connection() as session:
                user = session.execute(
                    text("SELECT * FROM candidates WHERE email = :email"),
                    {"email": email}
                ).fetchone()

                if not user:
                    return {"message": "Invalid email or password"}, 401

                if md5_hash_password(password) != user[3]:
                    return {"message": "Invalid email or password"}, 401

            payload = {
                "sub": email,
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }

            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

            return {
                "message": "Login successful",
                "user": {
                    "email": email,
                    "username": user[1],
                    "created_at": str(user[4]),
                    "updated_at": str(user[5])
                },
                "token": token
            }, 200

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return {"message": "Database error occurred"}, 500

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"message": "Unexpected error occurred"}, 500
