from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.database.connection import get_db_cursor
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Render the login page."""
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    username = request.form['username']
    password = request.form['password']
    
    # Check for admin login
    if username == "admin" and password == "admin":
        session['user_id'] = -1
        return redirect(url_for('admin.dashboard'))
    
    # Authenticate user
    user = User.authenticate(username, password)
    if user:
        session['user_id'] = user.user_id
        return redirect(url_for('poule.dashboard'))
    else:
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
            flash('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character', 'error')
            return render_template('createUser.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('createUser.html')
        
        # Check if username already exists
        with get_db_cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
                return render_template('createUser.html')
        
        # Register user
        User.register(username, password)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.index'))
    else:
        return render_template('createUser.html')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
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
    - Contains at least one special character
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
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True 