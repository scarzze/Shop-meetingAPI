from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import requests
import os

from model import db, Cart, CartItem

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///cart.db')
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

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5003')

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

# Helper function to get product details from product service
def get_product_details(product_id):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
        if response.status_code == 200:
            return response.json().get('product')
        return None
    except Exception as e:
        print(f"Error getting product details: {e}")
        return None

# Helper function to get or create cart
def get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
    return cart

@app.route('/')
def index():
    return {'message': 'Cart Service API'}

# Get cart
@app.route('/cart', methods=['GET'])
def get_cart():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({'cart': {'items': [], 'total': 0}}), 200
    
    items = [{
        'id': item.id,
        'product_id': item.product_id,
        'product_name': item.product_name,
        'product_image': item.product_image,
        'price': item.price,
        'quantity': item.quantity,
        'subtotal': item.price * item.quantity
    } for item in cart.items]
    
    total = sum(item['subtotal'] for item in items)
    
    return jsonify({
        'cart': {
            'id': cart.id,
            'user_id': cart.user_id,
            'items': items,
            'total': total
        }
    }), 200

# Add or update cart item
@app.route('/cart/items', methods=['POST'])
def add_to_cart():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    data = request.json
    
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id or not isinstance(product_id, int):
        return jsonify({'error': 'Valid product ID is required'}), 400
    
    if not quantity or not isinstance(quantity, int) or quantity < 1:
        return jsonify({'error': 'Quantity must be a positive integer'}), 400
    
    # Get product details from product service
    product = get_product_details(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if product is in stock
    if product.get('stock', 0) < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400
    
    # Get or create cart
    cart = get_or_create_cart(user_id)
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    
    if cart_item:
        # Update quantity
        cart_item.quantity = quantity
        cart_item.updated_at = datetime.utcnow()
    else:
        # Add new item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            price=product.get('price'),
            product_name=product.get('name'),
            product_image=product.get('image_url')
        )
        db.session.add(cart_item)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Product added to cart successfully',
        'cart_item': {
            'id': cart_item.id,
            'product_id': cart_item.product_id,
            'product_name': cart_item.product_name,
            'product_image': cart_item.product_image,
            'price': cart_item.price,
            'quantity': cart_item.quantity,
            'subtotal': cart_item.price * cart_item.quantity
        }
    }), 200

# Update cart item quantity
@app.route('/cart/items/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    data = request.json
    quantity = data.get('quantity')
    
    if not quantity or not isinstance(quantity, int):
        return jsonify({'error': 'Valid quantity is required'}), 400
    
    if quantity <= 0:
        # Remove item if quantity is 0 or negative
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart'}), 200
    
    # Get product details to check stock
    product = get_product_details(cart_item.product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if product is in stock
    if product.get('stock', 0) < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400
    
    # Update quantity
    cart_item.quantity = quantity
    cart_item.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Cart item updated successfully',
        'cart_item': {
            'id': cart_item.id,
            'product_id': cart_item.product_id,
            'product_name': cart_item.product_name,
            'product_image': cart_item.product_image,
            'price': cart_item.price,
            'quantity': cart_item.quantity,
            'subtotal': cart_item.price * cart_item.quantity
        }
    }), 200

# Remove item from cart
@app.route('/cart/items/<int:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart_item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'message': 'Item removed from cart successfully'}), 200

# Clear cart
@app.route('/cart', methods=['DELETE'])
def clear_cart():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    cart = Cart.query.filter_by(user_id=user_id).first()
    
    if not cart:
        return jsonify({'message': 'Cart is already empty'}), 200
    
    # Delete all items
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Cart cleared successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5004, debug=True)
