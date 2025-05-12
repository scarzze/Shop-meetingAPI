from datetime import datetime
from uuid import uuid4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect

db = SQLAlchemy()

class SerializerMixin:
    def to_dict(self, include_relationships=True, backref=None):
        """
        Generic method to serialize SQLAlchemy model to dictionary.
        - include_relationships: whether to include related objects.
        - backref: used internally to avoid recursion on backrefs.
        """
        result = {}
        mapper = inspect(self.__class__)
        for column in mapper.columns:
            value = getattr(self, column.key)
            if isinstance(value, datetime):
                result[column.key] = value.isoformat()
            else:
                result[column.key] = value

        if include_relationships:
            for name, relation in mapper.relationships.items():
                # Avoid recursion on backrefs
                if name == backref:
                    continue
                related_obj = getattr(self, name)
                if related_obj is None:
                    result[name] = None
                elif relation.uselist:
                    result[name] = [item.to_dict(include_relationships=include_relationships, backref=relation.back_populates) for item in related_obj]
                else:
                    result[name] = related_obj.to_dict(include_relationships=include_relationships, backref=relation.back_populates)
        return result


class User(SerializerMixin, db.Model):
    """Model for users synced from Auth Service"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, 
                           primaryjoin="User.id == Order.user_id",
                           foreign_keys='Order.user_id')


class Order(SerializerMixin, db.Model):
    """Model for customer orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.Integer, nullable=False, index=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Processing')
    shipping_address = db.Column(db.String(200), nullable=False)
    billing_address = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False, default='Pending')
    tracking_number = db.Column(db.String(50))
    estimated_delivery = db.Column(db.DateTime)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    returns = db.relationship('ReturnRequest', backref='order', lazy=True)

    STATUS_CHOICES = {
        'Processing': 'Order received, not yet shipped',
        'Shipped': 'Order has been shipped',
        'Delivered': 'Order delivered to customer',
        'Cancelled': 'Order cancelled before shipping',
        'Returned': 'Items returned by customer',
        'Refunded': 'Refund processed for returned/cancelled order'
    }

    def __repr__(self):
        return f'<Order {self.id} - Status: {self.status}>'

    def to_dict(self, include_relationships=True):
        data = super().to_dict(include_relationships=include_relationships)
        data['status_description'] = self.STATUS_CHOICES.get(self.status, '')
        data['item_count'] = len(self.items)
        return data


class OrderItem(SerializerMixin, db.Model):
    """Model for individual items within an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    return_status = db.Column(db.String(20), default='None')  # None, Requested, Returned, Refunded

    def __repr__(self):
        return f'<OrderItem {self.product_id} x {self.quantity} in Order {self.order_id}>'

    def to_dict(self, include_relationships=True):
        data = super().to_dict(include_relationships=include_relationships)
        data['total_price'] = self.quantity * (self.price - self.discount)
        return data


class ReturnRequest(SerializerMixin, db.Model):
    """Model for handling product returns"""
    __tablename__ = 'return_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime)
    reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    resolution = db.Column(db.String(200))
    refund_amount = db.Column(db.Float)
    refund_method = db.Column(db.String(50))
    items = db.relationship('ReturnItem', backref='return_request', lazy=True, cascade='all, delete-orphan')

    STATUS_CHOICES = {
        'Pending': 'Waiting for approval',
        'Approved': 'Return approved, awaiting items',
        'Rejected': 'Return rejected',
        'Received': 'Returned items received',
        'Refunded': 'Refund processed',
        'Completed': 'Return process completed'
    }

    def __repr__(self):
        return f'<ReturnRequest {self.id} for Order {self.order_id}>'

    def to_dict(self, include_relationships=True):
        data = super().to_dict(include_relationships=include_relationships)
        data['status_description'] = self.STATUS_CHOICES.get(self.status, '')
        return data


class ReturnItem(SerializerMixin, db.Model):
    """Model for individual items being returned"""
    __tablename__ = 'return_items'
    
    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('return_requests.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    condition = db.Column(db.String(50))  # New, Used, Damaged
    action = db.Column(db.String(50))  # Refund, Replace, Credit
    amount_refunded = db.Column(db.Float)

    def __repr__(self):
        return f'<ReturnItem {self.id} for Return {self.return_id}>'

    def to_dict(self, include_relationships=True):
        return super().to_dict(include_relationships=include_relationships)


class OrderStatusHistory(SerializerMixin, db.Model):
    """Model for tracking order status changes"""
    __tablename__ = 'order_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    changed_by = db.Column(db.String(50))  # Could be 'system', 'customer', or admin user ID
    notes = db.Column(db.String(200))

    def __repr__(self):
        return f'<OrderStatusHistory {self.id} for Order {self.order_id}>'

    def to_dict(self, include_relationships=True):
        data = super().to_dict(include_relationships=include_relationships)
        return data
