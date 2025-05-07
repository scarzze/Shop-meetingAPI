from flask import Blueprint

# Create blueprints
user_bp = Blueprint('user', __name__)
ticket_bp = Blueprint('ticket', __name__)
feedback_bp = Blueprint('feedback', __name__)
chat_bp = Blueprint('chat', __name__)

from .user_routes import user_bp
from .ticket_routes import ticket_bp
from .feedback_routes import feedback_bp
from .chat_routes import chat_bp

def register_routes(app):
    app.register_blueprint(user_bp, url_prefix='/api/v1')
    app.register_blueprint(ticket_bp, url_prefix='/api/v1')
    app.register_blueprint(feedback_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')