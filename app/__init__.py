from flask import Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config.default import *
import os

def create_app(config=None):
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load default configuration
    app.config.from_object('config.default')
    
    # Load environment specific configuration
    if config:
        app.config.from_object(config)
    
    # Initialize session handling
    Session(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Ensure instance and session directories exist
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Apply security headers to all responses
    @app.after_request
    def add_security_headers(response):
        # HTTP Strict Transport Security (HSTS)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy (CSP)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "font-src 'self'",
            "img-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'"
        ]
        response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # X-Content-Type-Options
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        response.headers['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy
        permissions = [
            'accelerometer=()',
            'camera=()',
            'geolocation=()',
            'gyroscope=()',
            'magnetometer=()',
            'microphone=()',
            'payment=()',
            'usb=()'
        ]
        response.headers['Permissions-Policy'] = ', '.join(permissions)
        
        # Cache-Control
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        
        return response
    
    # Register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.admin import admin_bp
    from app.controllers.poule import poule_bp
    from app.controllers.prediction import prediction_bp
    from app.controllers.results import results_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(poule_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(results_bp)
    
    return app 