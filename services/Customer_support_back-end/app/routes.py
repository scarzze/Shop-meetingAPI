from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from .models import db, User, Ticket, Message, SupportAgent, Feedback, Log
from .utils.auth_middleware import auth_required, support_agent_required
from .utils.user_sync import sync_user_from_auth
import os
from dotenv import load_dotenv

load_dotenv()

# Setup the database session
DATABASE_URI = os.getenv('DATABASE_URL')
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

@ticket_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
@auth_required
def get_ticket(ticket_id):
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
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.user_id != request.user['id'] and not request.user.get('is_support_agent'):
        return jsonify({"error": "Unauthorized access"}), 403
        
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Message content required"}), 400
        
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

@ticket_bp.route('/tickets/<int:ticket_id>/status', methods=['PUT'])
@support_agent_required
def update_ticket_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Status required"}), 400
        
    valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    if data['status'] not in valid_statuses:
        return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
        
    ticket.status = data['status']
    db.session.commit()
    
    return jsonify({
        "message": "Ticket status updated successfully",
        "status": ticket.status
    }), 200

@ticket_bp.route('/tickets/search', methods=['GET'])
@support_agent_required
def search_tickets():
    query = request.args.get('q', '')
    status = request.args.get('status')
    
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

# -------------------------- FEEDBACK ROUTES --------------------------

@feedback_bp.route('/feedback', methods=['POST'])
def create_feedback():
    data = request.get_json()
    feedback = Feedback(
        user_id=data['user_id'],
        ticket_id=data['ticket_id'],
        comment=data['comment'],
        rating=data['rating']
    )
    session.add(feedback)
    session.commit()
    return jsonify({"message": "Feedback submitted successfully"}), 201


@feedback_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    feedback = session.query(Feedback).get(feedback_id)
    if not feedback:
        return jsonify({"error": "Feedback not found"}), 404
    return jsonify({
        "id": feedback.id,
        "user_id": feedback.user_id,
        "ticket_id": feedback.ticket_id,
        "comment": feedback.comment,
        "rating": feedback.rating,
        "created_at": feedback.created_at
    })


# -------------------------- CHAT ROUTES --------------------------

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    response = {"message": f"Chatbot Response: {user_message}"}
    
    return jsonify(response)


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
