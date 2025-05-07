from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# User Model
class User(Base):
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

# Ticket Model
class Ticket(Base):
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
class Feedback(Base):
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
class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    ticket = relationship('Ticket', back_populates='logs')

    def __repr__(self):
        return f"<Log(id={self.id}, ticket_id={self.ticket_id}, message={self.message})>"

# Creating all the tables
def create_tables(engine):
    Base.metadata.create_all(engine)
 