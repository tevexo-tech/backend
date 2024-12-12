from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch PostgreSQL credentials from the environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Construct the DATABASE_URL using the environment variables
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Initialize SQLAlchemy engine
engine = create_engine(DATABASE_URL)

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
