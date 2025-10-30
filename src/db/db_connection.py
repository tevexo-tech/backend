# src/db/db_connection.py
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Fetch PostgreSQL credentials from the environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

logger.info("DB_HOST=%s DB_PORT=%s DB_NAME=%s DB_USER=%s", DB_HOST, DB_PORT, DB_NAME, DB_USER)

# Build a SQLAlchemy URL using URL.create() (handles encoding safely)
database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Create engine with pool_pre_ping to avoid stale connections
engine = create_engine(database_url, pool_pre_ping=True)

# Sessionmaker
Session = sessionmaker(bind=engine)

@contextmanager
def byte_master_connection(commit=False):
    """Open and return a database connection with optional commit."""
    session = Session()
    try:
        if commit:
            session.begin()
        yield session
        if commit:
            session.commit()
    except Exception as err:

        session.rollback()
        raise err
    finally:
        session.close()
