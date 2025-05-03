from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://BL4CK:Oversea838@localhost/customer_support'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add this for security
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    
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
