from flask import request
from extensions import socketio, db
from models import ChatMessage
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, leave_room

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if token:
        try:
            user_identity = decode_token(token)['sub']
            request.user_id = user_identity
        except Exception as e:
            return False  # Disconnect
    else:
        return False  # Disconnect

@socketio.on('join_chat')
def handle_join_chat(data):
    ticket_id = data.get('ticket_id')
    join_room(ticket_id)

@socketio.on('leave_chat')
def handle_leave_chat(data):
    ticket_id = data.get('ticket_id')
    leave_room(ticket_id)

@socketio.on('chat_message')
def handle_chat_message(data):
    ticket_id = data.get('ticket_id')
    user_id = data.get('user_id')
    message_text = data.get('message')

    message = ChatMessage(ticket_id=ticket_id, user_id=user_id, message=message_text)
    db.session.add(message)
    db.session.commit()

    emit('new_message', {'user_id': user_id, 'message': message_text}, room=ticket_id)
