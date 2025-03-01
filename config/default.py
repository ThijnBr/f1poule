import os
from datetime import timedelta

# Application settings
SECRET_KEY = 'your_secret_key_here'  # Change this in production!
WTF_CSRF_SECRET_KEY = 'your_csrf_key_here'  # Change this in production!
DEBUG = False
TESTING = False

# Session settings
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../instance/sessions')
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'f1poule_session_'

# Database settings
DB_CONFIG = {
    'database': 'poulef1',
    'user': 'postgres',
    'password': 'Broekie2004', 
    'host': 'localhost',
    'port': 5432,
    'connect_timeout': 10,
    'sslmode': 'disable'
} 