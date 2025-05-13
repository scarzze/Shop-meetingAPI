from app import app, db
from models import User

def seed_data():
    print("Seeding auth service database...")
    
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Create test users
    alice = User(
        username="alice",
        email="alice@example.com",
        password="password123"
    )
    
    bob = User(
        username="bob",
        email="bob@example.com",
        password="password123"
    )
    
    # Add users to database
    db.session.add(alice)
    db.session.add(bob)
    
    # Commit changes
    db.session.commit()
    
    print("Auth service database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        seed_data()
