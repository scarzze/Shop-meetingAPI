from flask import Blueprint, request, jsonify
from extensions import mail, db
from models import ContactMessage
from flask_mail import Message

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    try:
        # Save message to database
        message = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data.get('subject', 'Contact Form Submission'),
            message=data['message']
        )
        db.session.add(message)
        
        # Send confirmation email
        msg = Message('Contact Form Submission',
                     sender='noreply@shopmeet.com',
                     recipients=[data['email']])
        msg.body = f"Thank you for contacting us, {data['name']}!"
        mail.send(msg)
        
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
