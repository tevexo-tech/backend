# src/constants.py
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# 🔐 JWT & Flask secrets
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# 🗄️ Database config (optional, if needed in models)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "LocalDB")
DB_USER = os.getenv("DB_USER", "myapp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Sagar@1406")
