from flask_socketio import emit, join_room, leave_room
from app import socketio, db
from app.models import User, Ticket, Log
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.email import send_contact_email

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'status': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('error')
def handle_error(error):
    print(f'Socket.IO error: {error}')

# Contact Form Handler
@socketio.on('contact_form')
def handle_contact_form(data):
    try:
        # Create ticket
        ticket = Ticket(
            user_id=data.get('user_id'),
            subject=f"Contact Form: {data.get('subject')}",
            description=data.get('message')
        )
        db.session.add(ticket)
        db.session.commit()

        # Send email using Flask-Mail
        email_sent = send_contact_email(data)

        emit('contact_form_status', {
            'success': True,
            'ticket_id': ticket.id,
            'email_sent': email_sent
        })

    except Exception as e:
        print(f"Error processing contact form: {str(e)}")
        emit('contact_form_status', {
            'success': False,
            'error': str(e)
        })

# Live Chat Handlers
@socketio.on('join_chat')
@jwt_required()
def handle_join(data):
    current_user = get_jwt_identity()
    room = f"ticket_{data.get('ticket_id')}"
    join_room(room)
    emit('chat_joined', {
        'status': 'success',
        'user': current_user
    }, room=room)

@socketio.on('chat_message')
@jwt_required()
def handle_chat_message(data):
    try:
        current_user = get_jwt_identity()
        message = data.get('message', '')
        ticket_id = data.get('ticket_id')
        user_id = data.get('user_id')
        room = f"ticket_{ticket_id}"

        # Save to database
        log = Log(
            ticket_id=ticket_id,
            user_id=user_id,
            message=message,
            created_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

        # Emit to room
        emit('new_message', {
            'message': message,
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat()
        }, room=room)

    except Exception as e:
        print(f"Error handling chat message: {str(e)}")
        emit('error', {'message': 'Failed to process message'})

@socketio.on('leave_chat')
def handle_leave(data):
    """Handle user leaving a chat room"""
    ticket_id = data.get('ticket_id')
    room = f"ticket_{ticket_id}"
    leave_room(room)

# In email.py - Remove SendGrid related code
from flask_mail import Message
from app import mail
import os

def send_contact_email(data):
    try:
        msg = Message(
            subject=f"Contact Form: {data.get('subject', 'New Contact')}",
            recipients=[os.getenv('SUPPORT_EMAIL')],
            html=f"""
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {data.get('name')}</p>
                <p><strong>Email:</strong> {data.get('email')}</p>
                <p><strong>Message:</strong></p>
                <p>{data.get('message')}</p>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False