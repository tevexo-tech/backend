import hashlib

import jwt
from flask import Blueprint, request, jsonify
import datetime
from src.db.db_connection import byte_master_connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
import logging
import uuid
from src.config.constants import JWT_SECRET_KEY




JWT_SECRET_KEY=JWT_SECRET_KEY
logger = logging.getLogger(__name__)

auth_blueprint = Blueprint('auth', __name__)
def md5_hash_password(password: str) -> str:
    """Helper function to hash the password using MD5."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()


candidate_id = str(uuid.uuid4())  # Generate a unique UUID
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
            query = text("SELECT * FROM candidates WHERE username = :username OR email = :email")
            existing_user = session.execute(query, {'username': username, 'email': email}).fetchone()

            if existing_user:
                logger.error(f"User with username {username} or email {email} already exists in the database")
                return jsonify({"message": "Username or email already exists"}), 400

            hashed_password = md5_hash_password(password)
            candidate_id = str(uuid.uuid4())  # Generate a UUID for candidate_id

            insert_query = text(
                "INSERT INTO candidates (username, email, password_hash, candidate_id, created_at, updated_at) "
                "VALUES (:username, :email, :password_hash, :candidate_id, :created_at, :updated_at)"
            )

            session.execute(insert_query, {
                'username': username,
                'email': email,
                'password_hash': hashed_password,
                'candidate_id': candidate_id,
                'created_at': datetime.datetime.now(),
                'updated_at': datetime.datetime.now()
            })
            session.commit()

        logger.debug(f"User {username} created successfully")

        return jsonify({
            "message": "User created successfully",
            "user": {
                "username": username,
                "email": email,
                "candidate_id": candidate_id,
                "created_at": datetime.datetime.now(),
                "updated_at":datetime.datetime.now()
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
            query = text("SELECT * FROM candidates WHERE email = :email")
            user = session.execute(query, {'email': email}).fetchone()

            if not user:
                logger.error(f"User with email {email} does not exist")
                return jsonify({"message": "Invalid email or password"}), 401

            if md5_hash_password(password) != user[3]:
                logger.error(f"Incorrect password for email {email}")
                return jsonify({"message": "Invalid email or password"}), 401

        logger.debug(f"User with email {email} logged in successfully")

        # Generate JWT token
        payload = {
            'sub': email,  # Subject (usually user identifier)
            'iat': datetime.datetime.utcnow(),  # Issued at time
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiration time (1 hour)
        }

        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

        return jsonify({
            "message": "Login successful",
            "user": {
                "email": email,
                "username": user[1],
                "created_at": user[4],
                "updated_at": user[5]
            },
            "token": token  # Return the JWT token
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"Error occurred while interacting with the database: {str(e)}")
        return jsonify({"message": "An error occurred while logging in"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"message": "An unexpected error occurred"}), 500
