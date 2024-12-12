# application.py
from flask import Flask


app = Flask(__name__)

def register_blueprint(app):
    from src.api.authentications.authenticate import auth_blueprint
    from src.api.todo import to_do

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(to_do)
    return app


