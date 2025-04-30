from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

# Setup SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://BL4CK:Oversea838@localhost/customer_support'  # Use your actual URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Register routes (from routes.py)
from routes import register_routes
register_routes(app)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
