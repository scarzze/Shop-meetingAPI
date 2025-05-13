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
    # Try to use PostgreSQL, but fall back to SQLite if needed
    try:
        database_uri = os.getenv('DATABASE_URI', 'postgresql://victor:password123@localhost/customer_support_db')
        logger.info(f"Attempting to connect to database: {database_uri.split('@')[0].split('://')[0]}")
        
        # Test database connection before setting it
        from sqlalchemy import create_engine
        engine = create_engine(database_uri)
        connection = engine.connect()
        connection.close()
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        logger.info("Successfully connected to PostgreSQL database")
        
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {str(e)}")
        logger.info("Falling back to SQLite database")
        # Use SQLite as fallback with absolute path
        sqlite_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'customer_support.db')
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
    
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
        try:
            # Verify database connection
            with db.engine.connect() as connection:
                connection.execute("SELECT 1")
            db_status = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = f"error: {str(e)}"
        
        return {
            'status': 'healthy',
            'service': 'customer-support',
            'database': db_status,
            'version': '1.0.0'
        }, 200
        
    # Root endpoint for basic connectivity check
    @app.route('/')
    def root():
        return {'service': 'customer-support'}, 200
    
    logger.info("Customer Support Service initialization complete")
    return app

# Run the app
if __name__ == '__main__':
    app = create_app()
    socketio.run(app, port=5004, debug=True)
