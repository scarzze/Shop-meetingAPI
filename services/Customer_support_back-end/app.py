from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, mail, socketio
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes import chat
from flask_cors import CORS
from sqlalchemy import text

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)

    # Register error handlers
    register_error_handlers(app)

    # Add root route
    @app.route('/')
    def index():
        return jsonify({
            'service': 'Customer Support Service',
            'version': '1.0',
            'status': 'running',
            'endpoints': {
                'auth': '/register, /login',
                'contact': '/contact',
                'health': '/health'
            }
        })

    # Add health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Test database connection with proper SQL text formatting
            db.session.execute(text('SELECT 1'))
            return {'status': 'healthy', 'service': 'customer-support'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5004)
