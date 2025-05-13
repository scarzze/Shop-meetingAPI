from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- SupportTicket Model ---
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Reference to auth service user ID
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('SupportMessage', back_populates='ticket', cascade="all, delete-orphan", lazy=True)

# --- SupportMessage Model ---
class SupportMessage(db.Model):
    __tablename__ = 'support_messages'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)  # Reference to auth service user ID
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_staff = db.Column(db.Boolean, default=False)  # Flag to identify if message is from staff

    ticket = db.relationship('SupportTicket', back_populates='messages')
