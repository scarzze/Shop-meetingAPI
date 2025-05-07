from flask import Blueprint, request, jsonify
from extensions import mail, db
from flask_mail import Message

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.get_json()
    try:
        # Send confirmation email
        msg = Message('Contact Form Submission',
                     sender='noreply@shopmeet.com',
                     recipients=[data['email']])
        msg.body = f"Thank you for contacting us, {data['name']}!"
        mail.send(msg)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
