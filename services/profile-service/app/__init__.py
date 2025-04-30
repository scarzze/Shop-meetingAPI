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

    # register your blueprints only
    from app.routes.profile_routes import bp as profile_bp
    from app.routes.wishlist_routes import bp as wishlist_bp
    app.register_blueprint(profile_bp)
    app.register_blueprint(wishlist_bp)

    return app
