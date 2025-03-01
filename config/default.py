import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Default value for development only
WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'default_csrf_key')  # Default value for development only
DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
TESTING = False

# Session settings
SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'True').lower() == 'true'
PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.getenv('SESSION_LIFETIME_DAYS', '7')))
SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../instance/sessions')
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Strict')
SESSION_USE_SIGNER = os.getenv('SESSION_USE_SIGNER', 'True').lower() == 'true'
SESSION_KEY_PREFIX = os.getenv('SESSION_KEY_PREFIX', 'f1poule_session_')

# Database settings
DB_CONFIG = {
    'database': os.getenv('DB_NAME', 'poulef1'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),  # No default password for security
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', '10')),
    'sslmode': os.getenv('DB_SSL_MODE', 'disable')
} 