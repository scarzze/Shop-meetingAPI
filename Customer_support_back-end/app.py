from flask import Flask
from config import Config
from extensions import db, jwt, mail, socketio
from routes.auth import auth_bp
from routes.contact import contact_bp
from routes import chat  # Ensure chat routes are registered
from flask_cors import CORS

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

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5004,
        allow_unsafe_werkzeug=True  # This should be inside the function call, not outside
    )
