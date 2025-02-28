import os
from datetime import timedelta

# Application settings
SECRET_KEY = 'your_secret_key'  # Change this in production
DEBUG = False
TESTING = False

# Session settings
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../instance/sessions')

# Database settings
DB_CONFIG = {
    'database': 'poulef1',
    'user': 'postgres',
    'password': 'Broekie2004',  # Consider using environment variables for sensitive data
    'host': 'localhost',
    'connect_timeout': 10,
    'sslmode': 'disable'
} 