import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from email_validator import validate_email, EmailNotValidError
from services.auth.src.models import User
from shared.database import db, init_db
from services.auth.config.config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
init_db(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"],
    storage_uri="memory://"
)

def validate_email_address(email):
    try:
        if app.config['TESTING']:
            # Less strict validation for testing
            return email if '@' in email else None
        # Strict validation for production
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        return None

@app.route('/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = validate_email_address(data['email'])
        if not email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User()
        user.email = email
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in register: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'user': user.to_dict()}), 200
        
    except Exception as e:
        app.logger.error(f"Error in login: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/auth/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        app.logger.error(f"Error in verify token: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)