from flask import Blueprint, request, jsonify
from extensions import db, mail
from models import ContactMessage
from flask_mail import Message

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    message = ContactMessage(
        name=data['name'],
        email=data['email'],
        subject=data['subject'],
        message=data['message']
    )
    db.session.add(message)
    db.session.commit()

    # Send email
    msg = Message(subject=f"New Contact Message: {data['subject']}",
                  sender=data['email'],
                  recipients=['your_email@example.com'],
                  body=f"From: {data['name']} <{data['email']}>\n\n{data['message']}")
    mail.send(msg)

    return jsonify({'msg': 'Message sent successfully'}), 200
