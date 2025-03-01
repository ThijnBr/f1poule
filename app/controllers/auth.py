from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.database.connection import get_db_cursor
from app.utils.security_logger import log_login_attempt, log_registration, log_logout
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Render the login page or redirect to dashboard if logged in."""
    if 'user_id' in session:
        return redirect(url_for('poule.dashboard'))
    # Clear any existing flash messages when just viewing the page
    session.pop('_flashes', None)
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    username = request.form['username']
    password = request.form['password']
    
    # Authenticate user
    user = User.authenticate(username, password)
    if user:
        session['user_id'] = user.user_id
        session['is_admin'] = user.is_admin
        log_login_attempt(True, username)
        return redirect(url_for('poule.dashboard'))
    else:
        log_login_attempt(False, username)
        flash('Invalid username or password', 'error')
        return redirect(url_for('auth.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password
        if not is_password_valid(password):
            log_registration(False, username)
            flash('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number', 'error')
            return render_template('createUser.html')
        
        if password != confirm_password:
            log_registration(False, username)
            flash('Passwords do not match', 'error')
            return render_template('createUser.html')
        
        # Check if username already exists
        with get_db_cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                log_registration(False, username)
                flash('Username already exists', 'error')
                return render_template('createUser.html')
        
        # Register user
        User.register(username, password)
        log_registration(True, username)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.index'))
    else:
        # Clear any existing flash messages when just viewing the page
        session.pop('_flashes', None)
        return render_template('createUser.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    log_logout()
    session.pop('user_id', None)
    session.pop('poule', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.index'))

def is_password_valid(password):
    """
    Check if a password meets the complexity requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for at least one number
    if not re.search(r'[0-9]', password):
        return False
    
    return True 