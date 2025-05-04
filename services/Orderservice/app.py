from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from models import db, Order, OrderItem, ReturnRequest
from utils.auth_utils import auth_required, admin_required

def create_app(test_config=None):
    app = Flask(__name__)
    load_dotenv()
    
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
    
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
        
        # Email configuration
        app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER')
        app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', 587))
        app.config['EMAIL_ADDRESS'] = os.getenv('EMAIL_ADDRESS')
        app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    else:
        app.config.update(test_config)

    db.init_app(app)
    migrate = Migrate(app, db)

    # Helper Functions
    def send_email(to_email, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = app.config['EMAIL_ADDRESS']
            msg['To'] = to_email

            with smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT']) as server:
                server.starttls()
                server.login(app.config['EMAIL_ADDRESS'], app.config['EMAIL_PASSWORD'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


    def validate_json(required_fields):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not request.is_json:
                    return jsonify({'error': 'Request must be JSON'}), 400
                data = request.get_json()
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator

    # Endpoints
    @app.route('/orders/user/<int:user_id>', methods=['GET'])
    @auth_required
    def get_order_history(user_id):
        """Get order history for a specific user"""
        # Add security check to ensure users can only access their own orders
        current_user = request.user
        if current_user.get('id') != user_id and not current_user.get('is_admin', False):
            return jsonify({"error": "Unauthorized access"}), 403
        
        # If DEBUG_MODE is enabled, return mock order data
        debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        if debug_mode:
            # Return mock order data for testing
            mock_orders = [
                {
                    'id': 1,
                    'order_date': '2025-05-01T10:30:00',
                    'total_amount': 150.00,
                    'status': 'Delivered',
                    'items': [
                        {
                            'id': 1,
                            'product_id': 101,
                            'product_name': 'Wireless Mouse',
                            'quantity': 1,
                            'price': 25.00
                        },
                        {
                            'id': 2,
                            'product_id': 102,
                            'product_name': 'Mechanical Keyboard',
                            'quantity': 1,
                            'price': 125.00
                        }
                    ]
                },
                {
                    'id': 2,
                    'order_date': '2025-04-25T14:15:00',
                    'total_amount': 75.50,
                    'status': 'Processing',
                    'items': [
                        {
                            'id': 3,
                            'product_id': 103,
                            'product_name': 'USB-C Cable',
                            'quantity': 3,
                            'price': 15.00
                        }
                    ]
                }
            ]
            return jsonify(mock_orders)
        
        try:
            # Get all orders for the user
            orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
            
            # Convert orders to dict format
            order_list = []
            for order in orders:
                order_dict = {
                    'id': order.id,
                    'order_date': order.order_date.isoformat(),
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'items': [{
                        'id': item.id,
                        'product_id': item.product_id,
                        'product_name': item.product_name,
                        'quantity': item.quantity,
                        'price': float(item.price)
                    } for item in order.items]
                }
                order_list.append(order_dict)
                
            return jsonify(order_list)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/orders/<string:order_id>', methods=['GET'])
    @auth_required
    def get_order_details(order_id):
        """Get details for a specific order"""
        order = Order.query.get_or_404(order_id)
        
        # Verify user owns this order
        if order.user_id != request.user['id']:
            return jsonify({"error": "Unauthorized access"}), 403
        
        order_data = {
            'order_id': order.id,
            'user_id': order.user_id,
            'order_date': order.order_date.isoformat(),
            'total_amount': order.total_amount,
            'status': order.status,
            'shipping_address': order.shipping_address,
            'payment_method': order.payment_method,
            'items': [{
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.price
            } for item in order.items]
        }
        
        return jsonify(order_data), 200

    @app.route('/orders/<string:order_id>/status', methods=['GET'])
    @auth_required
    def get_order_status(order_id):
        """Get order status"""
        order = Order.query.get_or_404(order_id)
        
        # Verify user owns this order
        if order.user_id != request.user['id']:
            return jsonify({"error": "Unauthorized access"}), 403
            
        return jsonify({'status': order.status}), 200

    @app.route('/orders/<string:order_id>/status', methods=['PUT'])
    @admin_required
    def update_order_status(order_id):
        """Update order status (admin only)"""
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        # Validate status transition
        valid_transitions = {
            'Processing': ['Shipped', 'Cancelled'],
            'Shipped': ['Delivered', 'Returned'],
            'Delivered': ['Returned'],
            'Returned': ['Refunded'],
            'Cancelled': [],
            'Refunded': []
        }
        
        if new_status not in valid_transitions.get(order.status, []):
            return jsonify({'error': f'Invalid status transition from {order.status} to {new_status}'}), 400
        
        # Update status
        order.status = new_status
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Send notification if shipped
        if new_status == 'Shipped':
            user_email = f"user{order.user_id}@example.com"  # In production, get from user service
            subject = f"Your Order #{order.id} Has Shipped"
            body = (
                "Hello,\n\n"
                f"Your order #{order.id} has been shipped and is on its way to you.\n\n"
                f"Expected delivery date: {datetime.now().date()} (estimate)\n\n"
                "Thank you for shopping with us!"
            )
            send_email(user_email, subject, body)
        
        return jsonify({'message': 'Order status updated successfully'}), 200

    @app.route('/orders/<string:order_id>/cancel', methods=['POST'])
    @auth_required
    def cancel_order(order_id):
        """Request order cancellation"""
        order = Order.query.get_or_404(order_id)
        
        # Verify user owns this order
        if order.user_id != request.user['id']:
            return jsonify({"error": "Unauthorized access"}), 403
        
        if order.status not in ['Processing']:
            return jsonify({'error': 'Order cannot be cancelled at this stage'}), 400
        
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        # Update order status
        order.status = 'Cancelled'
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        return jsonify({'message': 'Order cancelled successfully'}), 200

    @app.route('/returns', methods=['POST'])
    @auth_required
    def request_return():
        """Request a return for an order"""
        data = request.get_json()
        if not data or 'order_id' not in data:
            return jsonify({"error": "Missing order_id"}), 400
            
        order = Order.query.get_or_404(data['order_id'])
        
        # Verify user owns this order
        if order.user_id != request.user['id']:
            return jsonify({"error": "Unauthorized access"}), 403
        
        # Validate order can be returned
        if order.status != 'Delivered':
            return jsonify({'error': 'Only delivered orders can be returned'}), 400
        
        # Check if return already exists
        existing_return = ReturnRequest.query.filter_by(order_id=data['order_id']).first()
        if existing_return:
            return jsonify({'error': 'Return already requested for this order'}), 400
        
        # Create return request
        return_request = ReturnRequest(
            order_id=data['order_id'],
            user_id=request.user['id'],
            reason=data.get('reason', 'No reason provided')
        )
        
        db.session.add(return_request)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        return jsonify({
            'message': 'Return request submitted successfully',
            'return_id': return_request.id
        }), 201

    @app.route('/returns/<int:return_id>', methods=['GET'])
    @auth_required
    def get_return_status(return_id):
        """Get status of a return request"""
        return_request = ReturnRequest.query.get_or_404(return_id)
        
        # Verify user owns this return request
        if return_request.user_id != request.user['id']:
            return jsonify({"error": "Unauthorized access"}), 403
        
        return_data = {
            'return_id': return_request.id,
            'order_id': return_request.order_id,
            'status': return_request.status,
            'request_date': return_request.request_date.isoformat(),
            'reason': return_request.reason,
            'resolution': return_request.resolution
        }
        
        return jsonify(return_data), 200

    @app.route('/returns/<int:return_id>/process', methods=['PUT'])
    @admin_required
    def process_return(return_id):
        """Process a return request (admin only)"""
        return_request = ReturnRequest.query.get_or_404(return_id)
        order = Order.query.get_or_404(return_request.order_id)
        
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'error': 'Action is required'}), 400
            
        action = data['action']
        resolution = data.get('resolution', '')
        
        if action == 'approve':
            return_request.status = 'Approved'
            return_request.resolution = resolution or 'Return approved'
            order.status = 'Returned'
            
        elif action == 'reject':
            return_request.status = 'Rejected'
            return_request.resolution = resolution or 'Return rejected'
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # Notify user
        user_email = f"user{return_request.user_id}@example.com"  # In production, get from user service
        subject = f"Update on Your Return Request #{return_request.id}"
        body = (
            "Hello,\n\n"
            f"Your return request for order #{order.id} has been {return_request.status.lower()}.\n\n"
            f"Resolution: {return_request.resolution}\n\n"
            "Thank you,\nCustomer Service"
        )
        
        send_email(user_email, subject, body)
        
        return jsonify({'message': f'Return request {action}ed successfully'}), 200

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'order'}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
