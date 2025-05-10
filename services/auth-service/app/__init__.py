from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .models.user import db
from .routes.auth_routes import auth_bp
from .commands import create_support_agent
from .utils.error_handlers import register_error_handlers
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure CORS with allowed origins
    CORS(app, resources={
        r"/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    })
    
    migrate = Migrate(app, db)
    
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register commands
    app.cli.add_command(create_support_agent)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @app.route('/health')
    def health_check():
        debug_mode = app.config.get('DEBUG_MODE', False)
        if debug_mode:
            return {
                'status': 'healthy', 
                'mode': 'debug',
                'message': 'Running in DEBUG_MODE with mock data'
            }, 200
        else:
            try:
                # Try a simple database query to validate connection
                db.session.execute('SELECT 1').fetchall()
                return {'status': 'healthy'}, 200
            except Exception as e:
                return {'status': 'unhealthy', 'error': str(e)}, 500
        
    return app