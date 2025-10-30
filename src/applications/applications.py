# src/applications/applications.py
from flask_cors import CORS

def register_blueprint(app):
    # Enable CORS globally (once)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Import the single routes blueprint and register it
    from routes import api_blueprint

    app.register_blueprint(api_blueprint)
    return app
