from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
import requests
import os

from models import db, UserProfile, PaymentMethod

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///profile.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

db.init_app(app)
Migrate(app, db)

# Configure CORS
allowed_origins = ["http://127.0.0.1:5173", "http://localhost:5173", "http://localhost:3000"]
frontend_url = os.getenv('FRONTEND_URL')
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

CORS(app, 
     resources={r"/*": {
         "origins": allowed_origins,
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
         "supports_credentials": True,
         "expose_headers": ["Authorization"]
     }},
     supports_credentials=True,
     allow_credentials=True
)

# Auth service URL
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')

# Helper function to validate token with auth service
def validate_token(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error validating token: {e}")
        return None

@app.route('/')
def index():
    return {'message': 'Profile Service API'}

# Get user profile
@app.route('/profile', methods=['GET'])
def get_user_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    payment_methods = [{
        'id': pm.id,
        'card_type': pm.card_type,
        'last_four': pm.last_four,
        'cardholder_name': pm.cardholder_name,
        'expiry_date': pm.expiry_date,
        'is_default': pm.is_default
    } for pm in profile.payment_methods]
    
    return jsonify({
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone': profile.phone,
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country,
            'payment_methods': payment_methods
        }
    }), 200

# Create or update user profile
@app.route('/profile', methods=['POST'])
def update_profile():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    data = request.json
    
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)
    
    # Update profile fields
    profile.first_name = data.get('first_name', profile.first_name)
    profile.last_name = data.get('last_name', profile.last_name)
    profile.phone = data.get('phone', profile.phone)
    profile.address_line1 = data.get('address_line1', profile.address_line1)
    profile.address_line2 = data.get('address_line2', profile.address_line2)
    profile.city = data.get('city', profile.city)
    profile.state = data.get('state', profile.state)
    profile.postal_code = data.get('postal_code', profile.postal_code)
    profile.country = data.get('country', profile.country)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'profile': {
            'id': profile.id,
            'user_id': profile.user_id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone': profile.phone,
            'address_line1': profile.address_line1,
            'address_line2': profile.address_line2,
            'city': profile.city,
            'state': profile.state,
            'postal_code': profile.postal_code,
            'country': profile.country
        }
    }), 200

# Get payment methods
@app.route('/payment-methods', methods=['GET'])
def get_payment_methods():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    payment_methods = [{
        'id': pm.id,
        'card_type': pm.card_type,
        'last_four': pm.last_four,
        'cardholder_name': pm.cardholder_name,
        'expiry_date': pm.expiry_date,
        'is_default': pm.is_default
    } for pm in profile.payment_methods]
    
    return jsonify({'payment_methods': payment_methods}), 200

# Add payment method
@app.route('/payment-methods', methods=['POST'])
def add_payment_method():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    data = request.json
    
    # Validate required fields
    required_fields = ['card_type', 'last_four', 'cardholder_name', 'expiry_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create new payment method
    payment_method = PaymentMethod(
        profile_id=profile.id,
        card_type=data['card_type'],
        last_four=data['last_four'],
        cardholder_name=data['cardholder_name'],
        expiry_date=data['expiry_date'],
        is_default=data.get('is_default', False)
    )
    
    # If this is the default payment method, update other payment methods
    if payment_method.is_default:
        for pm in profile.payment_methods:
            pm.is_default = False
    
    db.session.add(payment_method)
    db.session.commit()
    
    return jsonify({
        'message': 'Payment method added successfully',
        'payment_method': {
            'id': payment_method.id,
            'card_type': payment_method.card_type,
            'last_four': payment_method.last_four,
            'cardholder_name': payment_method.cardholder_name,
            'expiry_date': payment_method.expiry_date,
            'is_default': payment_method.is_default
        }
    }), 201

# Delete payment method
@app.route('/payment-methods/<int:payment_id>', methods=['DELETE'])
def delete_payment_method(payment_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    payment_method = PaymentMethod.query.filter_by(id=payment_id, profile_id=profile.id).first()
    
    if not payment_method:
        return jsonify({'error': 'Payment method not found'}), 404
    
    db.session.delete(payment_method)
    db.session.commit()
    
    return jsonify({'message': 'Payment method deleted successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002, debug=True)
