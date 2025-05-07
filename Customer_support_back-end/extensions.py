from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_socketio import SocketIO

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
