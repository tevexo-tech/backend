from flask import Flask
from src.applications.applications import register_blueprint

app = Flask(__name__)

# Register the auth blueprint
register_blueprint(app)

if __name__ == "__main__":
    app.run(debug=True)
