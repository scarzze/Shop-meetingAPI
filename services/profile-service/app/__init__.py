from flask import Flask
from flask_cors import CORS
from config import Config
from app.models import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    
    # Register blueprints
    from app.routes import (
        profile_routes, 
        wishlist_routes, 
        address_routes
    )
    
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(wishlist_routes.bp)
    app.register_blueprint(address_routes.bp)
    
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    return app