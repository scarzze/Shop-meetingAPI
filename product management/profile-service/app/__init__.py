from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    db.init_app(app)
    
    from app.routes import profile_routes, wishlist_routes
    app.register_blueprint(profile_routes.bp)
    app.register_blueprint(wishlist_routes.bp)
    
    return app