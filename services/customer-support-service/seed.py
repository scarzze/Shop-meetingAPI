from app import app, db
from models import SupportTicket, SupportMessage
from datetime import datetime, timedelta

with app.app_context():
    # Drop and recreate tables
    db.drop_all()
    db.create_all()

    # Create test support tickets
    # Ticket for Alice (user_id=1)
    ticket1 = SupportTicket(
        user_id=1,
        subject="Question about my order",
        message="I placed an order 3 days ago but haven't received any shipping confirmation. Can you help?",
        status="open",
        created_at=datetime.utcnow() - timedelta(days=3)
    )
    
    # Another ticket for Alice (user_id=1)
    ticket2 = SupportTicket(
        user_id=1,
        subject="Return policy question",
        message="What is your return policy for electronics?",
        status="closed",
        created_at=datetime.utcnow() - timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(days=8)
    )
    
    # Ticket for Bob (user_id=2)
    ticket3 = SupportTicket(
        user_id=2,
        subject="Product availability",
        message="When will the IPS LCD Gaming Monitor be back in stock?",
        status="open",
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    
    db.session.add_all([ticket1, ticket2, ticket3])
    db.session.flush()  # Get ticket IDs without committing
    
    # Add messages to tickets
    messages = [
        # Messages for ticket1
        SupportMessage(
            ticket_id=ticket1.id,
            sender_id=1,  # Alice
            message="I placed an order 3 days ago but haven't received any shipping confirmation. Can you help?",
            sent_at=datetime.utcnow() - timedelta(days=3)
        ),
        SupportMessage(
            ticket_id=ticket1.id,
            sender_id=999,  # Support staff
            message="Thank you for contacting us. I'll check the status of your order right away. Could you please provide your order number?",
            sent_at=datetime.utcnow() - timedelta(days=3, hours=2),
            is_staff=True
        ),
        SupportMessage(
            ticket_id=ticket1.id,
            sender_id=1,  # Alice
            message="My order number is #12345",
            sent_at=datetime.utcnow() - timedelta(days=2, hours=23)
        ),
        
        # Messages for ticket2
        SupportMessage(
            ticket_id=ticket2.id,
            sender_id=1,  # Alice
            message="What is your return policy for electronics?",
            sent_at=datetime.utcnow() - timedelta(days=10)
        ),
        SupportMessage(
            ticket_id=ticket2.id,
            sender_id=999,  # Support staff
            message="For electronics, we offer a 30-day return policy. Items must be in original packaging and in working condition. Would you like more details?",
            sent_at=datetime.utcnow() - timedelta(days=9, hours=12),
            is_staff=True
        ),
        SupportMessage(
            ticket_id=ticket2.id,
            sender_id=1,  # Alice
            message="No, that's all I needed to know. Thank you!",
            sent_at=datetime.utcnow() - timedelta(days=9, hours=10)
        ),
        SupportMessage(
            ticket_id=ticket2.id,
            sender_id=999,  # Support staff
            message="You're welcome! If you have any other questions, feel free to ask. I'll close this ticket for now.",
            sent_at=datetime.utcnow() - timedelta(days=8),
            is_staff=True
        ),
        
        # Messages for ticket3
        SupportMessage(
            ticket_id=ticket3.id,
            sender_id=2,  # Bob
            message="When will the IPS LCD Gaming Monitor be back in stock?",
            sent_at=datetime.utcnow() - timedelta(days=1)
        )
    ]
    
    db.session.add_all(messages)
    db.session.commit()
    
    print("Customer support service database seeded successfully.")
