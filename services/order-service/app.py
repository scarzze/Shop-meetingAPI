from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import requests
import os
import secrets

from models import db, Order, OrderItem, Payment

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///order.db')
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
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://localhost:5004')
PROFILE_SERVICE_URL = os.getenv('PROFILE_SERVICE_URL', 'http://localhost:5002')

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

# Helper function to get user's cart from cart service
def get_user_cart(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{CART_SERVICE_URL}/cart", headers=headers)
        if response.status_code == 200:
            return response.json().get('cart')
        return None
    except Exception as e:
        print(f"Error getting user cart: {e}")
        return None

# Helper function to clear user's cart after checkout
def clear_user_cart(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.delete(f"{CART_SERVICE_URL}/cart", headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"Error clearing user cart: {e}")
        return False

# Helper function to get user's profile from profile service
def get_user_profile(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{PROFILE_SERVICE_URL}/profile", headers=headers)
        if response.status_code == 200:
            return response.json().get('profile')
        return None
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

@app.route('/')
def index():
    return {'message': 'Order Service API'}

# Create order (checkout)
@app.route('/orders', methods=['POST'])
def checkout():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    data = request.json
    
    # Get shipping address from request or user profile
    shipping_address = data.get('shipping_address')
    if not shipping_address:
        profile = get_user_profile(token)
        if profile:
            address_parts = [
                profile.get('address_line1', ''),
                profile.get('address_line2', ''),
                profile.get('city', ''),
                profile.get('state', ''),
                profile.get('postal_code', ''),
                profile.get('country', '')
            ]
            shipping_address = ', '.join(filter(None, address_parts))
    
    if not shipping_address:
        return jsonify({'error': 'Shipping address is required'}), 400
    
    # Get payment method details
    payment_method = data.get('payment_method')
    if not payment_method:
        return jsonify({'error': 'Payment method is required'}), 400
    
    # Get cart items
    cart = get_user_cart(token)
    if not cart or not cart.get('items') or len(cart['items']) == 0:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Create order
    order = Order(
        user_id=user_id,
        shipping_address=shipping_address,
        total_amount=cart['total']
    )
    
    db.session.add(order)
    db.session.flush()  # Get order ID without committing
    
    # Add order items
    for item in cart['items']:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price_at_purchase=item['price'],
            product_name=item['product_name'],
            product_image=item['product_image']
        )
        db.session.add(order_item)
    
    # Create payment
    transaction_id = f"txn_{secrets.token_hex(16)}"
    payment = Payment(
        order_id=order.id,
        payment_method=payment_method,
        amount=cart['total'],
        status='Completed',
        transaction_id=transaction_id
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # Clear cart after successful order
    clear_user_cart(token)
    
    return jsonify({
        'message': 'Order created successfully',
        'order': {
            'id': order.id,
            'user_id': order.user_id,
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'shipping_address': order.shipping_address,
            'total_amount': order.total_amount,
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': item.price_at_purchase
            } for item in order.items],
            'payment': {
                'payment_method': payment.payment_method,
                'amount': payment.amount,
                'status': payment.status,
                'transaction_id': payment.transaction_id
            }
        }
    }), 201

# Get user orders
@app.route('/orders', methods=['GET'])
def get_orders():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    # Optional status filter
    status = request.args.get('status')
    
    if status:
        orders = Order.query.filter_by(user_id=user_id, status=status).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    return jsonify({
        'orders': [{
            'id': order.id,
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'shipping_address': order.shipping_address,
            'total_amount': order.total_amount,
            'items': [{
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_image': item.product_image,
                'quantity': item.quantity,
                'price': item.price_at_purchase
            } for item in order.items],
            'payment': {
                'payment_method': order.payment.payment_method if order.payment else None,
                'status': order.payment.status if order.payment else None
            }
        } for order in orders]
    }), 200

# Get order details
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({
        'order': {
            'id': order.id,
            'created_at': order.created_at.isoformat(),
            'status': order.status,
            'shipping_address': order.shipping_address,
            'total_amount': order.total_amount,
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_image': item.product_image,
                'quantity': item.quantity,
                'price': item.price_at_purchase,
                'subtotal': item.price_at_purchase * item.quantity
            } for item in order.items],
            'payment': {
                'id': order.payment.id if order.payment else None,
                'payment_method': order.payment.payment_method if order.payment else None,
                'amount': order.payment.amount if order.payment else None,
                'status': order.payment.status if order.payment else None,
                'paid_at': order.payment.paid_at.isoformat() if order.payment and order.payment.paid_at else None,
                'transaction_id': order.payment.transaction_id if order.payment else None
            }
        }
    }), 200

# Update order status
@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.json
    status = data.get('status')
    
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Validate status transitions
    valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    if status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
    
    # Prevent certain status transitions
    if order.status == 'Delivered' and status != 'Delivered':
        return jsonify({'error': 'Cannot change status of delivered orders'}), 400
    
    if order.status == 'Cancelled' and status != 'Cancelled':
        return jsonify({'error': 'Cannot change status of cancelled orders'}), 400
    
    order.status = status
    db.session.commit()
    
    return jsonify({
        'message': 'Order status updated successfully',
        'order': {
            'id': order.id,
            'status': order.status
        }
    }), 200

# Cancel order
@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Can only cancel pending or processing orders
    if order.status not in ['Pending', 'Processing']:
        return jsonify({'error': f'Cannot cancel order with status: {order.status}'}), 400
    
    order.status = 'Cancelled'
    db.session.commit()
    
    return jsonify({
        'message': 'Order cancelled successfully',
        'order': {
            'id': order.id,
            'status': order.status
        }
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5005, debug=True)
