from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from app.models import db
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
                'http://localhost:5006',  # Product service (this service)
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    })
    
    db.init_app(app)
    Migrate(app, db)
    
    # Register blueprints
    from app.routes import (
        product_routes,
        category_routes,
        review_routes,
        home_routes
    )
    
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(category_routes.bp)
    app.register_blueprint(review_routes.bp)
    
    @app.route('/health')
    def health_check():
        logger.debug("Health check received")
        return {'status': 'healthy', 'service': 'product'}, 200
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(e):
        logger.warning(f"404 error: {str(e)}")
        return {'error': 'Not Found', 'message': 'The requested resource does not exist'}, 404
        
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {str(e)}")
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500

    # Add error handler for validation errors
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"400 error: {str(e)}")
        return {'error': 'Bad Request', 'message': str(e)}, 400
        
    return app
