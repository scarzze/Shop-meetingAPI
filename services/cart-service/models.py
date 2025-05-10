from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)

    cart_items = db.relationship('CartItem', back_populates='user')
    orders = db.relationship('Order', back_populates='user')

class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    cart_items = db.relationship('CartItem', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')

class CartItem(db.Model):
    __tablename__ = 'cart_item'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', back_populates='cart_items')
    product = db.relationship('Product', back_populates='cart_items')

class Order(db.Model):
    __tablename__ = 'order'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    shipping_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Shipping and payment details
    shipping_address = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_country = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')
    
    status = db.Column(db.String(50), default='pending')

    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_item'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')