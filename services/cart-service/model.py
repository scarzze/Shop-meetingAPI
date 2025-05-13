from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- Cart Model ---
class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)  # Reference to auth service user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('CartItem', back_populates='cart', cascade="all, delete-orphan", lazy=True)


# --- CartItem Model ---
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # Reference to product service product ID
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Store price at time of adding to cart
    product_name = db.Column(db.String(120), nullable=False)  # Store product name
    product_image = db.Column(db.String(255))  # Store product image URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart = db.relationship('Cart', back_populates='items')

    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),)
