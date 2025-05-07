from flask_mail import Message
from flask import current_app
from app import mail
import os

def send_email(to_email, subject, html_content):
    """Generic email sending function"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_content,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_contact_email(data):
    """Send contact form submission email"""
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
            """,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False