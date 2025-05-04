import os

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Product, CartItem, Order, OrderItem
from utils.auth_utils import auth_required
from error_handlers import register_error_handlers
from utils.logging_utils import cart_logger as logger
from utils.user_sync import sync_user_from_auth

app = Flask(__name__)
load_dotenv()

logger.info("Starting Cart Service")

# Configure CORS with allowed origins
CORS(app, resources={
    r"/*": {
        "origins": [
            'http://localhost:5000',  # Main application
            'http://localhost:5001',  # Cart service
            'http://localhost:5002',  # Auth service
            'http://localhost:5003',  # Profile service
            'http://localhost:5004',  # Customer Support service
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logger.info("Configured database connection")
migrate = Migrate(app, db)

db.init_app(app)

# Register error handlers
register_error_handlers(app)
logger.info("Registered error handlers")

@app.route('/health')
def health_check():
    logger.debug("Health check endpoint called")
    return {'status': 'healthy', 'service': 'cart'}, 200

@app.route('/')
def index():
    logger.debug("Index endpoint called")
    return jsonify({'message': 'Welcome to the Shopping Cart API!'})

@app.route('/cart', methods=['GET'])
@auth_required
def get_all_cart_items():
    # Use authenticated user's ID from the request
    user_id = request.user['id']
    logger.debug(f"Getting all cart items for user {user_id}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    # Try to query the database
    try:
        items = CartItem.query.filter_by(user_id=user_id).all()
        cart = []
        for item in items:
            cart.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'price': item.product.price,
                'quantity': item.quantity,
                'subtotal': item.quantity * item.product.price
            })
        logger.info(f"Successfully retrieved {len(cart)} cart items for user {user_id}")
        return jsonify({'cart_items': cart})
    except Exception as e:
        logger.error(f"Error retrieving cart items: {str(e)}")
        # If database error occurs, use mock data in debug mode
        if debug_mode:
            # Return mock data for testing
            logger.warning("Using mock data in debug mode")
            mock_cart = []
            return jsonify({'cart_items': mock_cart})
        else:
            # In production, return the error
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/cart/<int:user_id>', methods=['GET'])
@auth_required
def get_cart(user_id):
    # Verify user is accessing their own cart
    request_user_id = request.user['id'] 
    logger.debug(f"Getting cart for user {user_id}, requested by user {request_user_id}")
    
    if user_id != request_user_id:
        logger.warning(f"Unauthorized access attempt: User {request_user_id} tried to access cart of user {user_id}")
        return jsonify({"error": "Unauthorized access"}), 403
    
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    try:
        items = CartItem.query.filter_by(user_id=user_id).all()
        cart = [{
            'product_id': item.product.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'subtotal': item.quantity * item.product.price
        } for item in items]

        total = sum(item['subtotal'] for item in cart)
        logger.info(f"Successfully retrieved cart with {len(cart)} items for user {user_id}")
        return jsonify({'cart': cart, 'total': total})
    except Exception as e:
        logger.error(f"Error retrieving cart: {str(e)}")
        # If database error occurs, use mock data in debug mode
        if debug_mode:
            # Return mock data for testing
            logger.warning("Using mock data in debug mode")
            mock_cart = [
                {
                    'product_id': 101,
                    'name': 'Sample Product',
                    'price': 29.99,
                    'quantity': 1,
                    'subtotal': 29.99
                }
            ]
            total = 29.99
            return jsonify({'cart': mock_cart, 'total': total})
        else:
            # In production, return the error
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/cart/add', methods=['POST'])
@auth_required
def add_to_cart():
    data = request.get_json()
    if not data or 'product_id' not in data:
        logger.warning("Missing required fields in add_to_cart request")
        return jsonify({'error': 'Missing required fields'}), 400
    
    user_id = request.user['id']
    logger.debug(f"Adding item to cart for user {user_id}: product_id={data['product_id']}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    try:
        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            logger.warning(f"Product {data['product_id']} not found")
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if item already in cart
        item = CartItem.query.filter_by(user_id=user_id, product_id=data['product_id']).first()
        
        if item:
            item.quantity += data.get('quantity', 1)
        else:
            item = CartItem(user_id=user_id, product_id=data['product_id'], quantity=data.get('quantity', 1))
            db.session.add(item)

        db.session.commit()
        logger.info(f"Successfully added item to cart: user_id={user_id}, product_id={data['product_id']}")
        return jsonify({'message': 'Item added to cart'})
    except Exception as e:
        # Roll back the session to avoid leaving it in a broken state
        db.session.rollback()
        logger.error(f"Error adding item to cart: {str(e)}")
        
        # If database error occurs, simulate success in debug mode
        if debug_mode:
            logger.warning("Using mock response in debug mode")
            return jsonify({'message': 'Item added to cart (DEBUG MODE)'})
        else:
            # In production, return the error
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/cart/update', methods=['PATCH'])
@auth_required
def update_cart():
    data = request.get_json()
    if not data or 'product_id' not in data:
        logger.warning("Missing required fields in update_cart request")
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = request.user['id']
    logger.debug(f"Updating cart for user {user_id}: product_id={data['product_id']}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    try:
        item = CartItem.query.filter_by(user_id=user_id, product_id=data['product_id']).first()
        if not item:
            logger.warning(f"Item not found in cart: user_id={user_id}, product_id={data['product_id']}")
            return jsonify({'error': 'Item not found in cart'}), 404

        # Update quantity if provided
        if 'quantity' in data:
            if data['quantity'] <= 0:
                logger.warning(f"Invalid quantity ({data['quantity']}) in update request")
                return jsonify({'error': 'Quantity must be greater than zero'}), 400
            item.quantity = data['quantity']

        db.session.commit()
        logger.info(f"Successfully updated cart: user_id={user_id}, product_id={data['product_id']}")

        return jsonify({'message': 'Cart updated successfully', 'item': {
            'product_id': item.product_id,
            'quantity': item.quantity
        }})
    except Exception as e:
        # Roll back the session to avoid leaving it in a broken state
        db.session.rollback()
        logger.error(f"Error updating cart: {str(e)}")
        
        # If database error occurs, simulate success in debug mode
        if debug_mode:
            logger.warning("Using mock response in debug mode")
            return jsonify({
                'message': 'Cart updated successfully (DEBUG MODE)', 
                'item': {
                    'product_id': data['product_id'],
                    'quantity': data.get('quantity', 1)
                }
            })
        else:
            # In production, return the error
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/checkout', methods=['POST'])
@auth_required
def checkout():
    user_id = request.user['id']
    logger.debug(f"Processing checkout for user {user_id}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    try:
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            logger.warning(f"Checkout attempted with empty cart: user_id={user_id}")
            return jsonify({'error': 'Cart is empty'}), 400

        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order(user_id=user_id, total=total)
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(order_item)
            db.session.delete(item)

        db.session.commit()
        logger.info(f"Checkout successful: user_id={user_id}, order_id={order.id}, total=${total}")
        return jsonify({'message': 'Order placed', 'order_id': order.id, 'total': total})
    except Exception as e:
        # Roll back the session to avoid leaving it in a broken state
        db.session.rollback()
        logger.error(f"Error during checkout: {str(e)}")
        
        # If database error occurs, simulate success in debug mode
        if debug_mode:
            # Create a mock successful response
            logger.warning("Using mock response in debug mode")
            mock_order_id = 12345
            mock_total = 199.99
            return jsonify({
                'message': 'Order placed (DEBUG MODE)', 
                'order_id': mock_order_id,
                'total': mock_total
            })
        else:
            # In production, return the error
            return jsonify({'error': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    logger.info(f"Starting server with debug={debug_mode}")
    app.run(debug=debug_mode, port=5001)