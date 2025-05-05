from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from dotenv import load_dotenv
import os
from .utils.error_handlers import register_error_handlers
from .models import db
from .utils.logging_utils import setup_logger

# Initialize extensions
migrate = Migrate()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    # Set up logging
    logger = setup_logger()
    app.logger = logger
    
    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://victor:password123@localhost/customer_support_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
    
    logger.info("Customer Support Service configuration loaded")
    
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
    
    logger.info("CORS configured")
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")
    
    logger.info("Flask extensions initialized")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints/routes
    with app.app_context():
        from .routes import register_routes
        register_routes(app)
        
        # Create database tables
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            # Don't fail on database errors - we have fallback mechanisms
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        logger.debug("Health check received")
        return {'status': 'healthy', 'service': 'customer-support'}, 200
    
    logger.info("Customer Support Service initialization complete")
    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    socketio.run(app, port=5004, debug=True)
