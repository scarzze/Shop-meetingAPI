from app import app, db
from models import UserProfile, PaymentMethod

with app.app_context():
    # Drop and recreate tables
    db.drop_all()
    db.create_all()

    # Create test user profiles
    profile1 = UserProfile(
        user_id=1,  # Corresponds to 'alice' in auth service
        first_name='Alice',
        last_name='Johnson',
        phone='555-123-4567',
        address_line1='123 Main St',
        address_line2='Apt 4B',
        city='New York',
        state='NY',
        postal_code='10001',
        country='USA'
    )
    
    profile2 = UserProfile(
        user_id=2,  # Corresponds to 'bob' in auth service
        first_name='Bob',
        last_name='Smith',
        phone='555-987-6543',
        address_line1='456 Oak Ave',
        city='San Francisco',
        state='CA',
        postal_code='94102',
        country='USA'
    )
    
    db.session.add_all([profile1, profile2])
    db.session.commit()
    
    # Add payment methods
    payment1 = PaymentMethod(
        profile_id=profile1.id,
        card_type='Visa',
        last_four='4242',
        cardholder_name='Alice Johnson',
        expiry_date='12/25',
        is_default=True
    )
    
    payment2 = PaymentMethod(
        profile_id=profile1.id,
        card_type='Mastercard',
        last_four='8765',
        cardholder_name='Alice Johnson',
        expiry_date='10/24',
        is_default=False
    )
    
    payment3 = PaymentMethod(
        profile_id=profile2.id,
        card_type='Amex',
        last_four='3456',
        cardholder_name='Bob Smith',
        expiry_date='08/26',
        is_default=True
    )
    
    db.session.add_all([payment1, payment2, payment3])
    db.session.commit()
    
    print("Profile service database seeded successfully.")
