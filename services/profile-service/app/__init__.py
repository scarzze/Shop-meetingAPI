from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app.models import db
from app.utils.error_handlers import register_error_handlers
import os
import logging
import datetime

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS with allowed origins
    CORS(app, resources={r"/*": {
        "origins": "*", 
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }})
    app.config['CORS_AUTOMATIC_OPTIONS'] = True
    
    db.init_app(app)
    Migrate(app, db)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Import and register our standalone health check blueprint FIRST
    # This ensures it takes precedence over any other routes with the same path
    from app.health_route import health_bp
    app.register_blueprint(health_bp)
    
    # Get route blueprints
    from app.routes import (
        profile_routes, 
        wishlist_routes, 
        address_routes,
        home_routes
    )
    
    # Register other blueprints
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(wishlist_routes.bp)
    app.register_blueprint(address_routes.bp)
    
    # Register the home_routes blueprint last since it has general routes
    app.register_blueprint(home_routes.bp)
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404 error: {str(e)}")
        return {'error': 'Not Found', 'message': 'The requested resource does not exist'}, 404
        
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {str(e)}")
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
        
    return app