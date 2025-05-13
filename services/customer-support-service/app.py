from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import requests
import os

from models import db, SupportTicket, SupportMessage

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///support.db')
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

# Initialize Socket.IO
if os.getenv('FLASK_ENV') == 'production':
    socketio = SocketIO(app, cors_allowed_origins=allowed_origins, supports_credentials=True, async_mode='threading')
else:
    socketio = SocketIO(app, cors_allowed_origins="*", supports_credentials=True, async_mode='threading')

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')

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

@app.route('/')
def index():
    return {'message': 'Customer Support Service API'}

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_chat')
def handle_join_chat(data):
    user_id = data.get('user_id')
    ticket_id = data.get('ticket_id')
    if user_id and ticket_id:
        join_room(str(ticket_id))
        emit('new_message', {'user_id': 'system', 'message': f'User {user_id} joined the chat'}, room=str(ticket_id))

@socketio.on('leave_chat')
def handle_leave_chat(data):
    ticket_id = data.get('ticket_id')
    if ticket_id:
        leave_room(str(ticket_id))

@socketio.on('chat_message')
def handle_chat_message(data):
    user_id = data.get('user_id')
    ticket_id = data.get('ticket_id')
    message_text = data.get('message')
    is_staff = data.get('is_staff', False)
    
    if user_id and ticket_id and message_text:
        # Save message to database
        ticket = SupportTicket.query.get(ticket_id)
        if ticket:
            message = SupportMessage(
                ticket_id=ticket_id,
                sender_id=user_id,
                message=message_text,
                is_staff=is_staff
            )
            db.session.add(message)
            db.session.commit()
            
            # Update ticket status and timestamp
            ticket.updated_at = datetime.utcnow()
            if ticket.status == 'closed':
                ticket.status = 'reopened'
            db.session.commit()
            
            # Broadcast message to room
            emit('new_message', {
                'id': message.id,
                'user_id': user_id,
                'message': message_text,
                'sent_at': message.sent_at.isoformat(),
                'is_staff': is_staff
            }, room=str(ticket_id))

@socketio.on('contact_form')
def handle_contact_form(data):
    try:
        user_id = data.get('user_id')
        subject = data.get('subject')
        message = data.get('message')
        
        if not user_id or not subject or not message:
            emit('contact_form_status', {'success': False, 'error': 'Missing required fields'})
            return
        
        # Create a new support ticket
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            message=message
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Create initial message
        support_message = SupportMessage(
            ticket_id=ticket.id,
            sender_id=user_id,
            message=message
        )
        db.session.add(support_message)
        db.session.commit()
        
        emit('contact_form_status', {'success': True, 'ticket_id': ticket.id})
    except Exception as e:
        emit('contact_form_status', {'success': False, 'error': str(e)})

# Create support ticket
@app.route('/tickets', methods=['POST'])
def submit_ticket():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    data = request.json
    
    subject = data.get('subject')
    message = data.get('message')
    
    if not subject or not message:
        return jsonify({'error': 'Subject and message are required'}), 400
    
    ticket = SupportTicket(
        user_id=user_id,
        subject=subject,
        message=message
    )
    db.session.add(ticket)
    db.session.commit()
    
    # Create initial message
    support_message = SupportMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        message=message
    )
    db.session.add(support_message)
    db.session.commit()
    
    return jsonify({
        'message': 'Support ticket created successfully',
        'ticket': {
            'id': ticket.id,
            'subject': ticket.subject,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat()
        }
    }), 201

# Get user tickets
@app.route('/tickets', methods=['GET'])
def get_tickets():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    # Optional status filter
    status = request.args.get('status')
    
    if status:
        tickets = SupportTicket.query.filter_by(user_id=user_id, status=status).order_by(SupportTicket.created_at.desc()).all()
    else:
        tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
    
    return jsonify({
        'tickets': [{
            'id': ticket.id,
            'subject': ticket.subject,
            'message': ticket.message,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat()
        } for ticket in tickets]
    }), 200

# Get ticket details
@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    messages = [{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'message': msg.message,
        'sent_at': msg.sent_at.isoformat(),
        'is_staff': msg.is_staff
    } for msg in ticket.messages]
    
    return jsonify({
        'ticket': {
            'id': ticket.id,
            'subject': ticket.subject,
            'message': ticket.message,
            'status': ticket.status,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat(),
            'messages': messages
        }
    }), 200

# Add message to ticket
@app.route('/tickets/<int:ticket_id>/messages', methods=['POST'])
def add_message(ticket_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    data = request.json
    message_text = data.get('message')
    
    if not message_text:
        return jsonify({'error': 'Message is required'}), 400
    
    # Create message
    message = SupportMessage(
        ticket_id=ticket_id,
        sender_id=user_id,
        message=message_text
    )
    db.session.add(message)
    
    # Update ticket status and timestamp
    ticket.updated_at = datetime.utcnow()
    if ticket.status == 'closed':
        ticket.status = 'reopened'
    
    db.session.commit()
    
    # Emit message to room via Socket.IO
    socketio.emit('new_message', {
        'id': message.id,
        'user_id': user_id,
        'message': message_text,
        'sent_at': message.sent_at.isoformat(),
        'is_staff': False
    }, room=str(ticket_id))
    
    return jsonify({
        'message': 'Message added successfully',
        'support_message': {
            'id': message.id,
            'sender_id': message.sender_id,
            'message': message.message,
            'sent_at': message.sent_at.isoformat(),
            'is_staff': message.is_staff
        }
    }), 201

# Close ticket
@app.route('/tickets/<int:ticket_id>/close', methods=['POST'])
def close_ticket(ticket_id):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    auth_data = validate_token(token)
    
    if not auth_data or not auth_data.get('valid'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = auth_data['user']['id']
    
    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()
    
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    
    ticket.status = 'closed'
    ticket.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Ticket closed successfully',
        'ticket': {
            'id': ticket.id,
            'status': ticket.status
        }
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5006, debug=True)
