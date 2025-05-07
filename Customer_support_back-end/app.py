from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, mail, socketio
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes import chat
from flask_cors import CORS
import eventlet 
import logging

eventlet.monkey_patch()
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    CORS(app, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(contact_bp)

    # Register socket events
    @socketio.on('connect')
    def handle_connect():
        app.logger.info('Client connected')
        return True

    @socketio.on('disconnect')
    def handle_disconnect():
        app.logger.info('Client disconnected')

    @socketio.on_error()
    def error_handler(e):
        app.logger.error(f'SocketIO error: {str(e)}')

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
    socketio.run(app, host='127.0.0.1', port=5004, debug=False, use_reloader=False)

