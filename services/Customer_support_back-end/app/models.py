from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())

    tickets = relationship('Ticket', back_populates='user')
    feedbacks = relationship('Feedback', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

# Support Agent Model
class SupportAgent(db.Model):
    __tablename__ = 'support_agents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    department = Column(String(100))
    is_available = Column(db.Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship('User', backref='agent_profile')

# Ticket Model
class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    status = Column(String(50), default='open')

    user = relationship('User', back_populates='tickets')
    logs = relationship('Log', back_populates='ticket')

    def __repr__(self):
        return f"<Ticket(id={self.id}, subject={self.subject}, user_id={self.user_id}, status={self.status})>"

# Feedback Model
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    comment = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship('User', back_populates='feedbacks')
    ticket = relationship('Ticket', back_populates='feedbacks')

    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, ticket_id={self.ticket_id}, rating={self.rating})>"

# Log Model
class Log(db.Model):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    ticket = relationship('Ticket', back_populates='logs')

    def __repr__(self):
        return f"<Log(id={self.id}, ticket_id={self.ticket_id}, message={self.message})>"

# Message Model
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'user' or 'agent'
    created_at = Column(DateTime, default=func.now())
    
    ticket = relationship('Ticket', backref='messages')
    sender = relationship('User')

# Creating all the tables
def create_tables(engine):
    db.create_all(engine)
