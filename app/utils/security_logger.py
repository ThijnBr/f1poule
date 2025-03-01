import logging
from datetime import datetime
from functools import wraps
from flask import request, session
import os

# Get current directory (where this script is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the log file path inside the app directory
log_file_path = os.path.join(current_directory, "security.log")

# Configure logging
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

security_file_handler = logging.FileHandler(log_file_path)
security_file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_file_handler.setFormatter(formatter)

security_logger.addHandler(security_file_handler)

def log_security_event(event_type, details, level=logging.INFO):
    """Log a security event with standardized formatting."""
    user_id = session.get('user_id', 'anonymous')
    ip_address = request.remote_addr
    
    message = f"[{event_type}] User ID: {user_id} - IP: {ip_address} - {details}"
    security_logger.log(level, message)

def log_login_attempt(success, username):
    """Log login attempts."""
    status = "SUCCESS" if success else "FAILED"
    log_security_event(
        "LOGIN_ATTEMPT",
        f"Status: {status} - Username: {username}",
        logging.INFO if success else logging.WARNING
    )

def log_password_change(success, user_id):
    """Log password change attempts."""
    status = "SUCCESS" if success else "FAILED"
    log_security_event(
        "PASSWORD_CHANGE",
        f"Status: {status}",
        logging.INFO if success else logging.WARNING
    )

def log_registration(success, username):
    """Log registration attempts."""
    status = "SUCCESS" if success else "FAILED"
    log_security_event(
        "REGISTRATION",
        f"Status: {status} - Username: {username}",
        logging.INFO if success else logging.WARNING
    )

def log_logout():
    """Log user logout."""
    log_security_event("LOGOUT", "User logged out successfully")

def log_csrf_violation():
    """Log CSRF token violations."""
    log_security_event(
        "CSRF_VIOLATION",
        "Invalid or missing CSRF token",
        logging.WARNING
    )

def log_session_manipulation():
    """Log potential session manipulation attempts."""
    log_security_event(
        "SESSION_MANIPULATION",
        "Potential session manipulation detected",
        logging.WARNING
    )
