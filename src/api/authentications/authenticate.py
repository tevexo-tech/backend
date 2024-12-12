import hashlib
from flask import Blueprint, request, jsonify
from datetime import datetime
from src.db.db_connection import byte_master_connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
import logging

logger = logging.getLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)
def md5_hash_password(password: str) -> str:
    """Helper function to hash the password using MD5."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()
@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            logger.error("Missing username, email, or password in request data")
            return jsonify({"message": "Username, email, and password are required"}), 400

        username = data['username']
        password = data['password']
        email = data['email']

        logger.debug(f"Checking if user {username} or email {email} already exists")

        with byte_master_connection() as session:
            query = text("SELECT * FROM users WHERE username = :username OR email = :email")
            existing_user = session.execute(query, {'username': username, 'email': email}).fetchone()

            if existing_user:
                logger.error(f"User with username {username} or email {email} already exists in the database")
                return jsonify({"message": "Username or email already exists"}), 400

            hashed_password = md5_hash_password(password)
            insert_query = text(
                "INSERT INTO users (username, email, password_hash, created_at, updated_at) "
                "VALUES (:username, :email, :password_hash, :created_at, :updated_at)"
            )

            session.execute(insert_query, {
                'username': username,
                'email': email,
                'password_hash': hashed_password,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            session.commit()

        logger.debug(f"User {username} created successfully")

        return jsonify({
            "message": "User created successfully",
            "user": {
                "username": username,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }), 201

    except SQLAlchemyError as e:
        logger.error(f"Error occurred while interacting with the database: {str(e)}")
        return jsonify({"message": "An error occurred while creating the user"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500


@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:

        data = request.get_json()

        if not data or not data.get('email') or not data.get('password'):
            logger.error("Missing email or password in request data")
            return jsonify({"message": "Email and password are required"}), 400

        email = data['email']
        password = data['password']

        logger.debug(f"Checking if user with email {email} exists")

        with byte_master_connection() as session:
            query = text("SELECT * FROM users WHERE email = :email")
            user = session.execute(query, {'email': email}).fetchone()

            if not user:
                logger.error(f"User with email {email} does not exist")
                return jsonify({"message": "Invalid email or password"}), 401

            if md5_hash_password(password) != user[3]:
                logger.error(f"Incorrect password for email {email}")
                return jsonify({"message": "Invalid email or password"}), 401

        logger.debug(f"User with email {email} logged in successfully")

        return jsonify({
            "message": "Login successful",
            "user": {
                "email": email,
                "username": user[1],
                "created_at": user[4],
                "updated_at": user[5]
            }
        }), 200

    except SQLAlchemyError as e:

        logger.error(f"Error occurred while interacting with the database: {str(e)}")
        return jsonify({"message": "An error occurred while logging in"}), 500

    except Exception as e:

        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500
