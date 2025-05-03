from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app.models import db
from app.utils.error_handlers import register_error_handlers

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure CORS with allowed origins
    CORS(app, resources={
        r"/*": {
            "origins": [
                'http://localhost:5000',  # Main application
                'http://localhost:5001',  # Cart service
                'http://localhost:5002',  # Auth service
                'http://localhost:5003',  # Profile service
                'http://localhost:5004',  # Customer Support service
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    })
    
    db.init_app(app)
    Migrate(app, db)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from app.routes import (
        profile_routes, 
        wishlist_routes, 
        address_routes,
        home_routes
    )
    
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(wishlist_routes.bp)
    app.register_blueprint(address_routes.bp)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'profile'}, 200
    
    return app