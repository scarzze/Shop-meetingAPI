from flask import Blueprint, request, jsonify
from models import User, Ticket, Feedback, Log
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

# Setup the database session
DATABASE_URI = 'postgresql://BL4CK:Oversea838@localhost/customer_support'  # Update as needed
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Blueprint setup for each section
user_bp = Blueprint('user', __name__)
ticket_bp = Blueprint('ticket', __name__)
feedback_bp = Blueprint('feedback', __name__)
chat_bp = Blueprint('chat', __name__)

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
def create_ticket():
    data = request.get_json()
    ticket = Ticket(
        user_id=data['user_id'],
        subject=data['subject'],
        description=data['description']
    )
    session.add(ticket)
    session.commit()
    return jsonify({"message": "Ticket created successfully"}), 201


@ticket_bp.route('/ticket/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = session.query(Ticket).get(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({
        "id": ticket.id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "created_at": ticket.created_at
    })


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
    
    # Here you can integrate the chatbot logic or send the message to another service
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
