from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    
    # Gmail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Use App Password from Gmail
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
    
    # Add support email to config
    app.config['SUPPORT_EMAIL'] = os.getenv('SUPPORT_EMAIL')
    
    # CORS configuration
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173"],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            'status': 401,
            'message': 'Unauthorized access'
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({
            'status': 401,
            'message': 'Token has expired'
        }), 401
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app,
        cors_allowed_origins=["http://localhost:3000", "http://localhost:5173"],
        async_mode='threading',
        ping_timeout=60
    )
    jwt.init_app(app)
    mail.init_app(app)
    
    # Import models
    from . import models
    
    # Register socket events
    from .routes import socket_routes
    
    # Register blueprints/routes
    with app.app_context():
        from .routes import register_routes
        register_routes(app)
        
        # Create database tables
        db.create_all()
    
    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)
