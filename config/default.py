import os
from datetime import timedelta

# Application settings
SECRET_KEY = 'f1poule'
WTF_CSRF_SECRET_KEY = 'f1poule'
DEBUG = False  # Always False in production
TESTING = False

# Session settings
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../instance/sessions')
SESSION_COOKIE_SECURE = True  # Set to True if using HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from Strict to Lax for better compatibility
SESSION_USE_SIGNER = True
SESSION_KEY_PREFIX = 'f1poule_session_'

# Database settings
DB_CONFIG = {
    'database': 'f1pouledev',
    'user': 'postgres',
    'password': 'Broekie.2004', 
    'host': '192.168.1.98',
    'port': 5432,
    'connect_timeout': 10,
    'sslmode': 'disable'
} 
