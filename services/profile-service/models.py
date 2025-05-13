from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- User Profile Model ---
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)  # Reference to auth service user ID
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Address fields
    address_line1 = db.Column(db.String(120))
    address_line2 = db.Column(db.String(120))
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(80))
    
    payment_methods = db.relationship('PaymentMethod', back_populates='user_profile', cascade="all, delete-orphan")


# --- PaymentMethod Model ---
class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('user_profiles.id'), nullable=False)
    card_type = db.Column(db.String(50))  # Visa, Mastercard, etc.
    last_four = db.Column(db.String(4))   # Last 4 digits of card
    cardholder_name = db.Column(db.String(100))
    expiry_date = db.Column(db.String(10))  # MM/YY format
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_profile = db.relationship('UserProfile', back_populates='payment_methods')
