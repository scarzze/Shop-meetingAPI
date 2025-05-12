from flask import Flask, jsonify, request
from config import Config
from extensions import db, jwt, mail, socketio
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes import chat
from flask_cors import CORS
import eventlet
import logging
import os
from flask_jwt_extended import decode_token
from models import ContactMessage
from sqlalchemy.exc import SQLAlchemyError

eventlet.monkey_patch()
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute('SELECT 1')
            return jsonify({'status': 'healthy'}), 200
        except SQLAlchemyError as e:
            app.logger.error(f'Database health check failed: {str(e)}')
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contact_bp, url_prefix='/api')

    # Register socket events
    @socketio.on('connect')
    def handle_connect():
        token = request.args.get('token')
        if not token:
            return False
        try:
            user_identity = decode_token(token)['sub']
            request.namespace.user_id = user_identity
            app.logger.info(f'Client connected: user_id={user_identity}')
        except Exception as e:
            app.logger.warning(f'Connection rejected: {str(e)}')
            return False

    @socketio.on('disconnect')
    def handle_disconnect():
        app.logger.info('Client disconnected')

    @socketio.on_error()
    def error_handler(e):
        app.logger.error(f'SocketIO error: {str(e)}')

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info('Database tables created successfully')
        except Exception as e:
            app.logger.error(f'Database initialization error: {str(e)}')

    return app

app = create_app()

@app.route("/")
def home():
    return jsonify({"message": "Server is up"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5004, debug=True)
