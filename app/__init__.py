from flask import Flask
from flask_session import Session
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
    
    # Initialize extensions
    Session(app)
    
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