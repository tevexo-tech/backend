# src/api/routes.py

from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS
# Import your resources (API classes)
from src.api.authentications.authenticate import SignupAPI, LoginAPI
from src.api.authentications.reset_password import ResetPassword
from src.api.todo import Todo

# ✅ Create one blueprint for all APIs
api_blueprint = Blueprint("api", __name__, url_prefix="/app/v1")
api = Api(api_blueprint)

# ✅ Register all resources here
api.add_resource(SignupAPI, "/signup")
api.add_resource(LoginAPI, "/login")
api.add_resource(ResetPassword, "/reset/password")

# Todo routes (POST, GET, DELETE)
api.add_resource(Todo, "/todo", "/todo/<int:id>")
