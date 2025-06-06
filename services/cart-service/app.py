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
from utils.service_utils import call_service

app = Flask(__name__)
CORS(app)
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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False  # Removed due to compatibility issues with Flask version

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

@app.route('/api/v1/carts', methods=['GET'])  # Standardized API path
@auth_required
def get_all_cart_items():
    user_id = request.user['id']
    logger.debug(f"Getting all cart items for user {user_id}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

    # In DEBUG_MODE, immediately return mock data without database operations
    if debug_mode:
        logger.warning("Using mock data in debug mode for cart items")
        # Mock cart data for testing
        mock_cart = [
            {
                'id': 1,
                'product_id': 101,
                'product_name': 'Smartphone XYZ',
                'price': 699.99,
                'quantity': 1,
                'subtotal': 699.99
            },
            {
                'id': 2,
                'product_id': 102,
                'product_name': 'Wireless Headphones',
                'price': 149.99,
                'quantity': 2,
                'subtotal': 299.98
            }
        ]
        return jsonify({'cart_items': mock_cart})

    # Not in DEBUG_MODE - attempt to use database
    try:
        # Sync user data from Auth Service
        sync_user_from_auth(request.user)
        
        # Query database for cart items
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
        return jsonify({'error': 'Could not retrieve cart items'}), 500

@app.route('/api/v1/carts/<int:user_id>', methods=['GET'])  # Standardized API path
def get_cart(user_id):
    request_user_id = request.user['id'] 
    logger.debug(f"Getting cart for user {user_id}, requested by user {request_user_id}")

    if user_id != request_user_id:
        logger.warning(f"Unauthorized access attempt: User {request_user_id} tried to access cart of user {user_id}")
        return jsonify({"error": "Unauthorized access"}), 403

    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

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
        if debug_mode:
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
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/v1/carts/items', methods=['POST'])  # Standardized API path
@auth_required
def add_to_cart():
    data = request.get_json()
    if not data or 'product_id' not in data:
        logger.warning("Missing required fields in add_to_cart request")
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = request.user['id']
    logger.debug(f"Adding item to cart for user {user_id}: product_id={data['product_id']}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock response without database operations
    if debug_mode:
        logger.warning("Using mock data in debug mode for add_to_cart")
        # Mock successful add response
        mock_response = {
            'success': True,
            'message': 'Item added to cart',
            'product': {
                'id': data['product_id'],
                'name': f"Product {data['product_id']}",
                'price': 49.99,
                'quantity': data.get('quantity', 1)
            }
        }
        return jsonify(mock_response), 201
        
    # Not in DEBUG_MODE - proceed with database operations
    try:
        # Sync user from auth service
        sync_user_from_auth(request.user)
        
        # Fetch product details from product-service
        product_service_url = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5006')
        product = call_service(product_service_url, f"/api/products/{data['product_id']}")

        if not product:
            logger.warning(f"Product {data['product_id']} not found in product-service")
            return jsonify({'error': 'Product not found'}), 404

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
        db.session.rollback()
        logger.error(f"Error adding item to cart: {str(e)}")
        if debug_mode:
            logger.warning("Using mock response in debug mode")
            return jsonify({'message': 'Item added to cart (DEBUG MODE)'})
        else:
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/cart/update', methods=['PATCH'])
@auth_required
def update_cart():
    data = request.get_json()
    if not data or 'product_id' not in data:
        logger.warning("Missing required fields in update_cart request")
        return jsonify({'error': 'Missing required fields'}), 400
        
    user_id = request.user['id']
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock response without database operations
    if debug_mode:
        logger.warning("Using mock data in debug mode for update_cart")
        # Mock successful update response
        mock_response = {
            'success': True,
            'message': 'Cart updated successfully',
            'updated_item': {
                'product_id': data['product_id'],
                'quantity': data.get('quantity', 1),
                'name': f"Product {data['product_id']}",
                'price': 49.99,
                'subtotal': 49.99 * data.get('quantity', 1)
            }
        }
        return jsonify(mock_response), 200

    user_id = request.user['id']
    logger.debug(f"Updating cart for user {user_id}: product_id={data['product_id']}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

    sync_user_from_auth(request.user)

    try:
        item = CartItem.query.filter_by(user_id=user_id, product_id=data['product_id']).first()
        if not item:
            logger.warning(f"Item not found in cart: user_id={user_id}, product_id={data['product_id']}")
            return jsonify({'error': 'Item not found in cart'}), 404

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
        db.session.rollback()
        logger.error(f"Error updating cart: {str(e)}")
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
            return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/checkout', methods=['POST'])
@auth_required
def checkout():
    user_id = request.user['id']
    logger.debug(f"Processing checkout for user {user_id}")
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock response without database operations
    if debug_mode:
        logger.warning("Using mock response in debug mode for checkout")
        # Generate mock order details
        mock_order_id = 12345
        mock_total = 199.99
        mock_items = [
            {
                'product_id': 101,
                'product_name': 'Smartphone XYZ',
                'quantity': 1,
                'price': 699.99,
                'subtotal': 699.99
            },
            {
                'product_id': 102,
                'product_name': 'Wireless Headphones',
                'quantity': 2,
                'price': 149.99,
                'subtotal': 299.98
            }
        ]
        return jsonify({
            'success': True,
            'message': 'Order placed successfully', 
            'order_id': mock_order_id,
            'total': mock_total,
            'items': mock_items
        }), 201
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        sync_user_from_auth(request.user)
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
        db.session.rollback()
        logger.error(f"Error during checkout: {str(e)}")
        if debug_mode:
            logger.warning("Using mock response in debug mode")
            mock_order_id = 12345
            mock_total = 199.99
            return jsonify({
                'message': 'Order placed (DEBUG MODE)', 
                'order_id': mock_order_id,
                'total': mock_total
            })
        else:
            return jsonify({'error': f'Database error: {str(e)}'}), 500

# Logic for calculating taxes, discounts, shipping costs, and generating order summaries

def calculate_order_summary(cart_items):
    subtotal = sum(item['subtotal'] for item in cart_items)
    tax_rate = float(os.getenv('TAX_RATE', 0.1))  # Default tax rate is 10%
    discount_rate = float(os.getenv('DISCOUNT_RATE', 0.05))  # Default discount rate is 5%
    shipping_cost = float(os.getenv('SHIPPING_COST', 10.0))  # Default shipping cost is $10

    tax = subtotal * tax_rate
    discount = subtotal * discount_rate
    total = subtotal + tax - discount + shipping_cost

    return {
        'subtotal': subtotal,
        'tax': tax,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'total': total
    }

@app.route('/cart/summary', methods=['GET'])
def get_cart_summary():
    user_id = request.user['id']
    logger.debug(f"Generating order summary for user {user_id}")

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

        order_summary = calculate_order_summary(cart)
        logger.info(f"Successfully generated order summary for user {user_id}")
        return jsonify({'cart': cart, 'order_summary': order_summary})
    except Exception as e:
        logger.error(f"Error generating order summary: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    logger.info(f"Starting server with debug={debug_mode}")
    app.run(host='0.0.0.0', debug=debug_mode, port=5001)
