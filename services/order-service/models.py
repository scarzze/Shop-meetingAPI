from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --- Order Model ---
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Reference to auth service user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")
    shipping_address = db.Column(db.Text)
    total_amount = db.Column(db.Float, nullable=False)

    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan", lazy=True)
    payment = db.relationship('Payment', back_populates='order', uselist=False, cascade="all, delete-orphan")


# --- OrderItem Model ---
class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)  # Reference to product service product ID
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_purchase = db.Column(db.Float, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)  # Store product name
    product_image = db.Column(db.String(255))  # Store product image URL

    order = db.relationship('Order', back_populates='items')


# --- Payment Model ---
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    transaction_id = db.Column(db.String(120), unique=True, nullable=False)

    order = db.relationship('Order', back_populates='payment')
