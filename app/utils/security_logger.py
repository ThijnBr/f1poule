import logging
import os
from datetime import datetime
from functools import wraps
from flask import request, session

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create file handler for security logs
security_file_handler = logging.FileHandler('logs/security.log')
security_file_handler.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
security_file_handler.setFormatter(formatter)

# Add the handler to the logger
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