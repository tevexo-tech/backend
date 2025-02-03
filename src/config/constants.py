import os
from dotenv import dotenv_values
from os.path import join, dirname

# Define the path to your .env file
secret_config_path = join(dirname(__file__), '../.env')  # Relative to utils/ folder

# Load environment variables from .env file and os.environ
config = {
    **dotenv_values(dotenv_path=secret_config_path),
    **os.environ
}

# Helper function to load configuration
def cfg_load(x, default=None):
    return config.get(x, default)

# Helper function to convert string to boolean
def str2bool(x):
    return x.lower() in ['true', '1', 'y', 'yes']

# Load JWT_SECRET_KEY from the config
JWT_SECRET_KEY = config['JWT_SECRET_KEY']  # Ensure JWT_SECRET_KEY is set in your .env
