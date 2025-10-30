import datetime
import logging

from flask import request
from flask_restful import Resource
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.api.authentications.authenticate import md5_hash_password
from src.db.db_connection import byte_master_connection

logger = logging.getLogger(__name__)
class ResetPassword(Resource):
    def post(self):
        try:
            data = request.get_json()
            if not data or not data.get("email") or not data.get("new_password"):
                return {"message": "Email and new password are required"}, 400

            email = data["email"]
            new_password = data["new_password"]

            hashed_password = md5_hash_password(new_password)

            with byte_master_connection() as session:
                # Check if user exists
                user = session.execute(
                    text("SELECT * FROM candidates WHERE email = :email"),
                    {"email": email}
                ).fetchone()

                if not user:
                    return {"message": "User not found"}, 404

                # Update password
                session.execute(
                    text("""
                        UPDATE candidates 
                        SET password = :password, updated_at = :updated_at
                        WHERE email = :email
                    """),
                    {
                        "password": hashed_password,
                        "updated_at": datetime.datetime.now(),
                        "email": email
                    }
                )
                session.commit()

            return {"message": "Password updated successfully"}, 200

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return {"message": "Database error occurred"}, 500

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"message": "Unexpected error occurred"}, 500
