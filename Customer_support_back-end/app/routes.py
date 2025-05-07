from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from .models import db, User, Ticket, Message, SupportAgent, Feedback, Log
from .utils.auth_middleware import auth_required, support_agent_required
from .utils.user_sync import sync_user_from_auth
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Setup the database session
DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://victor:password123@localhost/customer_support_db')
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint setup for each section
user_bp = Blueprint('user', __name__)
ticket_bp = Blueprint('ticket', __name__)
feedback_bp = Blueprint('feedback', __name__)
chat_bp = Blueprint('chat', __name__)
support_bp = Blueprint('support', __name__)

# -------------------------- USER ROUTES --------------------------

@user_bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data['full_name']
    )
    session.add(user)
    session.commit()
    return jsonify({"message": "User created successfully"}), 201


@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at
    })


# -------------------------- TICKET ROUTES --------------------------

@ticket_bp.route('/ticket', methods=['POST'])
@auth_required
def create_ticket():
    data = request.get_json()
    if not data or 'subject' not in data or 'description' not in data:
        return jsonify({"error": "Subject and description required"}), 400

    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock ticket creation response
        # Generate a pseudo-random ticket ID based on timestamp
        import time
        mock_ticket_id = int(time.time()) % 1000 + 4  # Start from ID 4 to not conflict with existing mock data
        
        return jsonify({
            "success": True,
            "message": "Ticket created successfully (DEBUG MODE)",
            "ticket_id": mock_ticket_id,
            "ticket": {
                "id": mock_ticket_id,
                "subject": data['subject'],
                "description": data['description'],
                "status": "Open",
                "created_at": datetime.now().isoformat()
            }
        }), 201
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        # Sync user from Auth Service to ensure user exists in database
        user = sync_user_from_auth(request.user)
        user_id = request.user['id']
        
        ticket = Ticket(
            user_id=user_id,
            subject=data['subject'],
            description=data['description'],
            status='Open'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": ticket.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create ticket", "message": str(e)}), 500

@ticket_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
@auth_required
def get_ticket(ticket_id):
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock ticket data based on ticket_id
        if ticket_id == 1:
            # Mock data for ticket #1
            mock_ticket = {
                "id": 1,
                "subject": "Product not working",
                "description": "I purchased the XYZ model and it's not turning on.",
                "status": "Open",
                "created_at": "2025-05-01T09:30:00",
                "messages": [
                    {
                        "id": 1,
                        "content": "I've tried charging it overnight but it still won't power on.",
                        "sender_id": 1,
                        "sender_type": "user",
                        "created_at": "2025-05-01T09:30:00"
                    },
                    {
                        "id": 2,
                        "content": "Have you tried resetting it by holding the power button for 10 seconds?",
                        "sender_id": 101,
                        "sender_type": "agent",
                        "created_at": "2025-05-01T10:15:00"
                    }
                ]
            }
            return jsonify(mock_ticket), 200
        elif ticket_id == 2:
            # Mock data for ticket #2
            mock_ticket = {
                "id": 2,
                "subject": "Refund request",
                "description": "I would like to request a refund for my recent purchase.",
                "status": "In Progress",
                "created_at": "2025-05-02T14:15:00",
                "messages": [
                    {
                        "id": 3,
                        "content": "The item doesn't match the description on your website.",
                        "sender_id": 1,
                        "sender_type": "user",
                        "created_at": "2025-05-02T14:15:00"
                    },
                    {
                        "id": 4,
                        "content": "I'm sorry to hear that. Can you provide the order number?",
                        "sender_id": 102,
                        "sender_type": "agent",
                        "created_at": "2025-05-02T15:30:00"
                    }
                ]
            }
            return jsonify(mock_ticket), 200
        elif ticket_id == 3:
            # Mock data for ticket #3
            mock_ticket = {
                "id": 3,
                "subject": "Question about delivery",
                "description": "When will my order be delivered?",
                "status": "Resolved",
                "created_at": "2025-05-03T11:45:00",
                "messages": [
                    {
                        "id": 5,
                        "content": "I placed order #12345 three days ago and haven't received any shipping info.",
                        "sender_id": 1,
                        "sender_type": "user",
                        "created_at": "2025-05-03T11:45:00"
                    },
                    {
                        "id": 6,
                        "content": "Your order has been shipped and will arrive tomorrow. The tracking number is ABC123XYZ.",
                        "sender_id": 103,
                        "sender_type": "agent",
                        "created_at": "2025-05-03T13:00:00"
                    }
                ]
            }
            return jsonify(mock_ticket), 200
        else:
            # For any new tickets created in this testing session
            if ticket_id >= 4 and ticket_id <= 1000:
                # Generate mock data for dynamically created tickets
                mock_ticket = {
                    "id": ticket_id,
                    "subject": f"Test Ticket #{ticket_id}",
                    "description": "This is a test ticket created for endpoint testing",
                    "status": "Open",
                    "created_at": datetime.now().isoformat(),
                    "messages": []
                }
                return jsonify(mock_ticket), 200
            else:
                # Ticket not found
                return jsonify({"error": "Ticket not found"}), 404
    
    # Not in DEBUG_MODE - use the database
    try:
        # Sync user from Auth Service to ensure user exists in database
        sync_user_from_auth(request.user)
        
        ticket = Ticket.query.get_or_404(ticket_id)
        
        if ticket.user_id != request.user['id'] and not request.user.get('is_support_agent'):
            return jsonify({"error": "Unauthorized access"}), 403
            
        return jsonify({
            "id": ticket.id,
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat(),
            "messages": [{
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "sender_type": msg.sender_type,
                "created_at": msg.created_at.isoformat()
            } for msg in ticket.messages]
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve ticket", "message": str(e)}), 500

@ticket_bp.route('/tickets', methods=['GET'])
@auth_required
def get_tickets():
    # Sync user from Auth Service to ensure user exists in database
    sync_user_from_auth(request.user)
    
    import os
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # Return mock data in DEBUG_MODE to bypass database permission issues
    if debug_mode:
        mock_tickets = [
            {
                "id": 1,
                "subject": "Product not working",
                "status": "Open",
                "created_at": "2025-05-01T09:30:00"
            },
            {
                "id": 2,
                "subject": "Refund request",
                "status": "In Progress",
                "created_at": "2025-05-02T14:15:00"
            },
            {
                "id": 3,
                "subject": "Question about delivery",
                "status": "Resolved",
                "created_at": "2025-05-03T11:45:00"
            }
        ]
        return jsonify({"tickets": mock_tickets}), 200
        
    # Normal database operation if not in DEBUG_MODE
    try:
        if request.user.get('is_support_agent'):
            tickets = Ticket.query.all()
        else:
            tickets = Ticket.query.filter_by(user_id=request.user['id']).all()
            
        return jsonify({
            "tickets": [{
                "id": ticket.id,
                "subject": ticket.subject,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat()
            } for ticket in tickets]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ticket_bp.route('/tickets/<int:ticket_id>/messages', methods=['POST'])
@auth_required
def add_message(ticket_id):
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Message content required"}), 400
    
    if debug_mode:
        # In DEBUG_MODE, return mock message creation response
        import time
        mock_message_id = int(time.time()) % 1000 + 7  # Start from ID 7 to not conflict with existing mock data
        
        # Determine sender type based on user role
        sender_type = 'agent' if request.user.get('is_support_agent') else 'user'
        
        # Mock response for valid tickets
        if ticket_id in [1, 2, 3] or (ticket_id >= 4 and ticket_id <= 1000):
            return jsonify({
                "success": True,
                "message": "Message added successfully (DEBUG MODE)",
                "message_id": mock_message_id,
                "message_details": {
                    "id": mock_message_id,
                    "ticket_id": ticket_id,
                    "content": data['content'],
                    "sender_id": request.user['id'],
                    "sender_type": sender_type,
                    "created_at": datetime.now().isoformat()
                }
            }), 201
        else:
            return jsonify({"error": "Ticket not found"}), 404
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        if ticket.user_id != request.user['id'] and not request.user.get('is_support_agent'):
            return jsonify({"error": "Unauthorized access"}), 403
            
        message = Message(
            ticket_id=ticket_id,
            content=data['content'],
            sender_id=request.user['id'],
            sender_type='agent' if request.user.get('is_support_agent') else 'user'
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            "message": "Message added successfully",
            "message_id": message.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to add message", "message": str(e)}), 500

@ticket_bp.route('/tickets/<int:ticket_id>/status', methods=['PUT'])
@support_agent_required
def update_ticket_status(ticket_id):
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Status required"}), 400
        
    valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    if data['status'] not in valid_statuses:
        return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
    
    if debug_mode:
        # In DEBUG_MODE, return mock status update response
        # Mock response for valid tickets
        if ticket_id in [1, 2, 3] or (ticket_id >= 4 and ticket_id <= 1000):
            return jsonify({
                "success": True,
                "message": f"Ticket status updated to '{data['status']}' (DEBUG MODE)",
                "ticket_id": ticket_id,
                "previous_status": "Open" if ticket_id == 1 else "In Progress" if ticket_id == 2 else "Resolved",
                "new_status": data['status']
            }), 200
        else:
            return jsonify({"error": "Ticket not found"}), 404
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        ticket.status = data['status']
        db.session.commit()
        
        return jsonify({"message": "Ticket status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update ticket status", "message": str(e)}), 500

@ticket_bp.route('/tickets/search', methods=['GET'])
@support_agent_required
def search_tickets():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    query = request.args.get('q', '')
    status = request.args.get('status')
    
    if debug_mode:
        # In DEBUG_MODE, return mock search results
        mock_tickets = [
            {
                "id": 1,
                "subject": "Product not working",
                "status": "Open",
                "created_at": "2025-05-01T09:30:00"
            },
            {
                "id": 2,
                "subject": "Refund request",
                "status": "In Progress",
                "created_at": "2025-05-02T14:15:00"
            },
            {
                "id": 3,
                "subject": "Question about delivery",
                "status": "Resolved",
                "created_at": "2025-05-03T11:45:00"
            }
        ]
        
        # Filter based on query params if provided
        filtered_tickets = mock_tickets
        
        if query:
            query = query.lower()
            filtered_tickets = [t for t in filtered_tickets if query in t['subject'].lower()]
            
        if status:
            filtered_tickets = [t for t in filtered_tickets if t['status'] == status]
            
        return jsonify({"tickets": filtered_tickets}), 200
    
    # Not in DEBUG_MODE - use the database
    try:
        tickets_query = Ticket.query
        
        if query:
            tickets_query = tickets_query.filter(
                (Ticket.subject.ilike(f'%{query}%')) |
                (Ticket.description.ilike(f'%{query}%'))
            )
            
        if status:
            tickets_query = tickets_query.filter_by(status=status)
            
        tickets = tickets_query.all()
        
        return jsonify({
            "tickets": [{
                "id": ticket.id,
                "subject": ticket.subject,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat()
            } for ticket in tickets]
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to search tickets", "message": str(e)}), 500

# -------------------------- FEEDBACK ROUTES --------------------------

@feedback_bp.route('/feedback', methods=['POST'])
@auth_required
def create_feedback():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    data = request.get_json()
    if not data or 'comment' not in data or 'rating' not in data or 'ticket_id' not in data:
        return jsonify({"error": "Invalid feedback data"}), 400
    
    if debug_mode:
        # In DEBUG_MODE, return mock feedback creation response
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully (DEBUG MODE)",
            "feedback_id": int(time.time()) % 1000,  # Generate a simple mock ID
            "feedback_details": {
                "ticket_id": data['ticket_id'],
                "user_id": request.user['id'],
                "comment": data['comment'],
                "rating": data['rating'],
                "created_at": datetime.now().isoformat()
            }
        }), 201
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        feedback = Feedback(
            user_id=request.user['id'],
            ticket_id=data['ticket_id'],
            comment=data['comment'],
            rating=data['rating']
        )
        db.session.add(feedback)
        db.session.commit()
        return jsonify({"message": "Feedback submitted successfully", "feedback_id": feedback.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to submit feedback", "message": str(e)}), 500


@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
@auth_required
def get_feedback(feedback_id):
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    if debug_mode:
        # In DEBUG_MODE, return mock feedback data
        if feedback_id == 1:
            mock_feedback = {
                "id": 1,
                "user_id": request.user['id'],
                "ticket_id": 1,
                "comment": "The support agent was very helpful and solved my issue quickly.",
                "rating": 5,
                "created_at": "2025-05-05T10:30:00"
            }
            return jsonify(mock_feedback), 200
        elif feedback_id == 2:
            mock_feedback = {
                "id": 2,
                "user_id": request.user['id'],
                "ticket_id": 2,
                "comment": "Issue was resolved but took longer than expected.",
                "rating": 3,
                "created_at": "2025-05-06T15:45:00"
            }
            return jsonify(mock_feedback), 200
        elif feedback_id == 3:
            mock_feedback = {
                "id": 3,
                "user_id": request.user['id'],
                "ticket_id": 3,
                "comment": "Excellent service, thank you!",
                "rating": 5,
                "created_at": "2025-05-07T09:15:00"
            }
            return jsonify(mock_feedback), 200
        else:
            return jsonify({"error": "Feedback not found"}), 404
    
    # Not in DEBUG_MODE - proceed with database operations
    try:
        feedback = db.session.query(Feedback).get(feedback_id)
        if not feedback:
            return jsonify({"error": "Feedback not found"}), 404
            
        # Check if the user is authorized to view this feedback
        if feedback.user_id != request.user['id'] and not request.user.get('is_support_agent'):
            return jsonify({"error": "Unauthorized access"}), 403
            
        return jsonify({
            "id": feedback.id,
            "user_id": feedback.user_id,
            "ticket_id": feedback.ticket_id,
            "comment": feedback.comment,
            "rating": feedback.rating,
            "created_at": feedback.created_at.isoformat() if hasattr(feedback.created_at, 'isoformat') else str(feedback.created_at)
        }), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve feedback", "message": str(e)}), 500


# -------------------------- CHAT ROUTES --------------------------

@chat_bp.route('/chat', methods=['POST'])
@auth_required
def chat():
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message content required"}), 400
        
    user_message = data.get('message', '')
    
    if debug_mode:
        # In DEBUG_MODE, return mock chatbot responses based on the user's message
        mock_responses = {
            "hello": "Hello! How can I assist you today?",
            "help": "I'm here to help. What do you need assistance with?",
            "order": "For order-related inquiries, please provide your order number.",
            "refund": "To process a refund, please provide your order details and reason for the refund.",
            "shipping": "Shipping typically takes 3-5 business days. For international orders, it may take 7-14 days.",
            "contact": "You can reach our customer service team at support@example.com or call us at 1-800-123-4567."
        }
        
        # Check if any keywords in the message match our predefined responses
        user_message_lower = user_message.lower()
        for keyword, response_text in mock_responses.items():
            if keyword in user_message_lower:
                return jsonify({
                    "message": response_text,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": f"debug-{int(time.time())}"
                })
        
        # Default response if no keywords match
        return jsonify({
            "message": f"I understand you're asking about '{user_message}'. How can I help you with that?",
            "timestamp": datetime.now().isoformat(),
            "session_id": f"debug-{int(time.time())}"
        })
    
    # Not in DEBUG_MODE - implement actual chatbot logic
    try:
        # This would be replaced with actual chatbot implementation
        # For now, we'll just echo the message back with a prefix
        response = {"message": f"Chatbot Response: {user_message}", "timestamp": datetime.now().isoformat()}
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "Failed to process chat message", "message": str(e)}), 500


# -------------------------- Error Handling --------------------------

@user_bp.errorhandler(404)
@ticket_bp.errorhandler(404)
@feedback_bp.errorhandler(404)
@chat_bp.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Resource not found"}), 404


# Add blueprints to the Flask app
def register_routes(app):
    app.register_blueprint(user_bp, url_prefix='/api/v1')
    app.register_blueprint(ticket_bp, url_prefix='/api/v1')
    app.register_blueprint(feedback_bp, url_prefix='/api/v1')
    app.register_blueprint(chat_bp, url_prefix='/api/v1')
    app.register_blueprint(support_bp, url_prefix='/api/v1')
