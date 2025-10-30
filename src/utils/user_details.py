import jwt
from flask import request
from sqlalchemy.sql import text
from src.db.db_connection import byte_master_connection
from src.utils.constant import JWT_SECRET, JWT_ALGORITHM

class AuthError(Exception):
    """Generic auth error to be raised by UserDetails."""
    def __init__(self, message, code=401):
        super().__init__(message)
        self.code = code

class UserDetails:
    @staticmethod
    def get_current_user():
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthError("Missing or invalid token", 401)

        token = auth_header.split(" ", 1)[1]
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise
        except jwt.InvalidTokenError:
            raise AuthError("Invalid token", 401)

        email_or_sub = decoded.get("sub") or decoded.get("email") or decoded.get("candidate_id") or decoded.get("user_id")
        if not email_or_sub:
            raise AuthError("Invalid token payload", 400)

        try:
            with byte_master_connection() as session:
                query = text("""
                    SELECT id, candidate_id, username, email
                    FROM candidates
                    WHERE email = :val OR candidate_id::text = :val OR id::text = :val
                    LIMIT 1
                """)
                result = session.execute(query, {"val": str(email_or_sub)}).fetchone()

                if not result:
                    raise AuthError("User not found", 404)

                user = {
                    "id": result[0],
                    "candidate_id": str(result[1]),
                    "username": result[2],
                    "email": result[3]
                }
                return user

        except AuthError:
            raise
        except Exception as e:
            # unexpected DB error
            raise Exception(f"Unexpected DB error: {e}")
