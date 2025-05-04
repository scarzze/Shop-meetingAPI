import os

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Product, CartItem, Order, OrderItem

app = Flask(__name__)
CORS(app)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Shopping Cart API!'})

@app.route('/cart', methods=['GET'])
def get_all_cart_items():
    items = CartItem.query.all()
    cart = []
    for item in items:
        cart.append({
            'id': item.id,
            'user_id': item.user_id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'subtotal': item.quantity * item.product.price
        })
    return jsonify({'cart_items': cart})

@app.route('/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    items = CartItem.query.filter_by(user_id=user_id).all()
    cart = [{
        'product_id': item.product.id,
        'name': item.product.name,
        'price': item.product.price,
        'quantity': item.quantity,
        'subtotal': item.quantity * item.product.price
    } for item in items]

    total = sum(item['subtotal'] for item in cart)
    return jsonify({'cart': cart, 'total': total})

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    if not data or 'user_id' not in data or 'product_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if 'quantity' in data and data['quantity'] <= 0:
        return jsonify({'error': 'Quantity must be greater than zero'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'Invalid user ID'}), 400

    product = Product.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Invalid product ID'}), 400

    # Check if the item already exists in the cart
    item = CartItem.query.filter_by(user_id=data['user_id'], product_id=data['product_id']).first()
    if item:
        item.quantity += data.get('quantity', 1)
    else:
        item = CartItem(user_id=data['user_id'], product_id=data['product_id'], quantity=data.get('quantity', 1))
        db.session.add(item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart'})

@app.route('/cart/update', methods=['PATCH'])
def update_cart():
    data = request.json
    if not data or 'user_id' not in data or 'product_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    item = CartItem.query.filter_by(user_id=data['user_id'], product_id=data['product_id']).first()
    if not item:
        return jsonify({'error': 'Item not found in cart'}), 404

    # Update quantity if provided
    if 'quantity' in data:
        if data['quantity'] <= 0:
            return jsonify({'error': 'Quantity must be greater than zero'}), 400
        item.quantity = data['quantity']

    db.session.commit()

    return jsonify({'message': 'Cart updated successfully', 'item': {
        'product_id': item.product_id,
        'quantity': item.quantity
    }})

@app.route('/cart/remove', methods=['DELETE'])
def remove_from_cart():
    data = request.json
    if not data or 'user_id' not in data or 'product_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    item = CartItem.query.filter_by(
        user_id=data['user_id'], 
        product_id=data['product_id']
    ).first()
    
    if not item:
        return jsonify({'error': 'Item not found in cart'}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item removed from cart'})

@app.route('/cart/apply-discount', methods=['POST'])
def apply_discount():
    data = request.json
    if not data or 'user_id' not in data or 'discount_code' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Discount validation logic here
    discount_amount = 0.0
    if data['discount_code'] == 'WELCOME10':
        discount_amount = 0.10  # 10% discount
    
    return jsonify({
        'discount_applied': bool(discount_amount),
        'discount_amount': discount_amount
    })

@app.route('/checkout/<int:user_id>', methods=['POST'])
def checkout(user_id):
    data = request.json
    if not data:
        return jsonify({'error': 'Missing request data'}), 400

    required_fields = [
        'shipping_address', 'shipping_city', 'shipping_country',
        'shipping_postal_code', 'payment_method'
    ]
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing shipping or payment details'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user ID'}), 400

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Validate stock availability
    for item in cart_items:
        if item.quantity > item.product.stock:
            return jsonify({
                'error': f'Insufficient stock for {item.product.name}',
                'available': item.product.stock
            }), 400

    # Calculate totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    discount = subtotal * float(data.get('discount_amount', 0))
    shipping_fee = 10.0  # Add shipping fee calculation logic
    total = subtotal - discount + shipping_fee

    # Create order
    order = Order(
        user_id=user_id,
        subtotal=subtotal,
        discount=discount,
        shipping_fee=shipping_fee,
        total=total,
        shipping_address=data['shipping_address'],
        shipping_city=data['shipping_city'],
        shipping_country=data['shipping_country'],
        shipping_postal_code=data['shipping_postal_code'],
        payment_method=data['payment_method']
    )
    db.session.add(order)
    db.session.flush()

    # Create order items and update stock
    order_items = []
    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )
        order_items.append(order_item)
        
        # Update product stock
        item.product.stock -= item.quantity
        
        # Remove from cart
        db.session.delete(item)

    db.session.add_all(order_items)
    db.session.commit()

    return jsonify({
        'message': 'Order placed successfully',
        'order': {
            'id': order.id,
            'subtotal': subtotal,
            'discount': discount,
            'shipping_fee': shipping_fee,
            'total': total,
            'items': [{
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': item.quantity * item.price
            } for item in order_items],
            'shipping_address': order.shipping_address,
            'shipping_city': order.shipping_city,
            'shipping_country': order.shipping_country,
            'shipping_postal_code': order.shipping_postal_code,
            'payment_method': order.payment_method,
            'status': order.status
        }
    })

@app.route('/checkout/<int:user_id>', methods=['POST'])
def checkout(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Invalid user ID'}), 400

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
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
    return jsonify({'message': 'Order placed', 'order_id': order.id, 'total': total})

if __name__ == '__main__':
    app.run(port=5000,debug=True)