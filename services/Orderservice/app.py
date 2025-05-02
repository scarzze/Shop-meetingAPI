from flask import Flask, jsonify, request
from flask_migrate import Migrate
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from models import db, Order, OrderItem, ReturnRequest

def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://orderservice_user:orderservice_pass@localhost:5432/orderservice_db'
    else:
        app.config.update(test_config)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    # Email configuration (replace with your actual email settings)
    app.config['SMTP_SERVER'] = 'smtp.example.com'
    app.config['SMTP_PORT'] = 587
    app.config['EMAIL_ADDRESS'] = 'your_email@example.com'
    app.config['EMAIL_PASSWORD'] = 'your_password'

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
    def get_order_history(user_id):
        """Get order history for a specific user"""
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
        
        order_list = []
        for order in orders:
            order_data = {
                'order_id': order.id,
                'order_date': order.order_date.isoformat(),
                'total_amount': order.total_amount,
                'status': order.status,
                'items': [{
                    'product_id': item.product_id,
                    'quantity': item.quantity,
                    'price': item.price
                } for item in order.items]
            }
            order_list.append(order_data)
        
        return jsonify({'orders': order_list}), 200

    @app.route('/orders/<string:order_id>', methods=['GET'])
    def get_order_details(order_id):
        """Get details for a specific order"""
        order = Order.query.get_or_404(order_id)
        
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

    @app.route('/orders/<string:order_id>/status', methods=['GET', 'PUT'])
    def order_status(order_id):
        """Get or update order status"""
        order = Order.query.get_or_404(order_id)
        
        if request.method == 'GET':
            return jsonify({'status': order.status}), 200
        
        elif request.method == 'PUT':
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
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
                # In a real app, you would get the user's email from the user service
                user_email = f"user{order.user_id}@example.com"
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
    @validate_json([])
    def cancel_order(order_id):
        """Request order cancellation"""
        order = Order.query.get_or_404(order_id)
        
        if order.status not in ['Processing']:
            return jsonify({'error': 'Order cannot be cancelled at this stage'}), 400
        
        data = request.get_json()
        reason = data.get('reason', 'No reason provided')
        
        # Update order status
        order.status = 'Cancelled'
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        
        # In a real app, you would process the refund here
        # For now, we'll just log it
        print(f"Order {order_id} cancelled. Refund should be processed for amount {order.total_amount}")
        
        return jsonify({'message': 'Order cancelled successfully'}), 200

    @app.route('/returns', methods=['POST'])
    @validate_json(['order_id', 'user_id', 'reason'])
    def request_return():
        """Request a return for an order or item"""
        data = request.get_json()
        order_id = data.get('order_id')
        user_id = data.get('user_id')
        reason = data.get('reason')
        
        order = Order.query.get_or_404(order_id)
        
        # Validate order can be returned
        if order.status != 'Delivered':
            return jsonify({'error': 'Only delivered orders can be returned'}), 400
        
        # Check if return already exists
        existing_return = ReturnRequest.query.filter_by(order_id=order_id).first()
        if existing_return:
            return jsonify({'error': 'Return already requested for this order'}), 400
        
        # Create return request
        return_request = ReturnRequest(
            order_id=order_id,
            user_id=user_id,
            reason=reason
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
    def get_return_status(return_id):
        """Get status of a return request"""
        return_request = ReturnRequest.query.get_or_404(return_id)
        
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
    @validate_json(['action'])
    def process_return(return_id):
        """Process a return request (admin only)"""
        # In a real app, you would check admin permissions here
        return_request = ReturnRequest.query.get_or_404(return_id)
        order = Order.query.get_or_404(return_request.order_id)
        
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'
        resolution = data.get('resolution', '')
        
        if action == 'approve':
            return_request.status = 'Approved'
            return_request.resolution = resolution or 'Return approved'
            
            # Update order status
            order.status = 'Returned'
            
            # Process refund (in a real app, you would integrate with payment gateway)
            print(f"Refund processed for order {order.id}, amount: {order.total_amount}")
            
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
        user_email = f"user{return_request.user_id}@example.com"
        subject = f"Update on Your Return Request #{return_request.id}"
        body = (
            "Hello,\n\n"
            f"Your return request for order #{order.id} has been {return_request.status.lower()}.\n\n"
            f"Resolution: {return_request.resolution}\n\n"
            "Thank you,\nCustomer Service"
        )
        
        send_email(user_email, subject, body)
        
        return jsonify({'message': f'Return request {action}ed successfully'}), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
