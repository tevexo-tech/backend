# application.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

def register_blueprint(app):
    CORS(app, resources={r"/*": {"origins": "*"}})
    from src.api.authentications.authenticate import auth_blueprint
    from src.api.todo import to_do

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(to_do)
    return app


