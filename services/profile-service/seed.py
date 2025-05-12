from datetime import datetime
from app import create_app, db
from app.models import Profile, Address, WishlistItem
import os

app = create_app()
app.app_context().push()

def seed_data():
    # Create tables if they don't exist
    db.create_all()

    # Create test profiles
    profiles = [
        {
            'user_id': 'test_user_1',
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferences': {
                'favorite_categories': ['Electronics', 'Books'],
                'preferred_price_range': {'min': 0, 'max': 1000}
            },
            'notification_settings': {
                'email_marketing': True,
                'order_updates': True,
                'price_alerts': True,
                'new_products': False,
                'recommendations': True
            }
        },
        {
            'user_id': 'test_user_2',
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '+0987654321',
            'preferences': {
                'favorite_categories': ['Fashion', 'Home'],
                'preferred_price_range': {'min': 0, 'max': 500}
            }
        }
    ]

    created_profiles = []
    for profile_data in profiles:
        # Check if profile exists
        profile = Profile.query.filter_by(user_id=profile_data['user_id']).first()
        if not profile:
            profile = Profile(**profile_data)
            db.session.add(profile)
            print(f"Created new profile for {profile_data['user_id']}")
        else:
            # Update existing profile
            for key, value in profile_data.items():
                setattr(profile, key, value)
            print(f"Updated existing profile for {profile_data['user_id']}")
        created_profiles.append(profile)
    db.session.commit()

    # Add addresses
    addresses = [
        {
            'profile_id': created_profiles[0].id,
            'address_type': 'shipping',
            'is_default': True,
            'name': 'John Doe',
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'country': 'USA',
            'postal_code': '10001',
            'phone': '+1234567890'
        },
        {
            'profile_id': created_profiles[0].id,
            'address_type': 'billing',
            'is_default': True,
            'name': 'John Doe',
            'street': '123 Main St',
            'city': 'New York',
            'state': 'NY',
            'country': 'USA',
            'postal_code': '10001',
            'phone': '+1234567890'
        }
    ]

    # Clear existing addresses
    for profile in created_profiles:
        Address.query.filter_by(profile_id=profile.id).delete()
    
    for address_data in addresses:
        address = Address(**address_data)
        db.session.add(address)
    db.session.commit()
    print("Updated addresses")

    # Add wishlist items
    wishlist_items = [
        {
            'profile_id': created_profiles[0].id,
            'product_id': 'product_1'
        },
        {
            'profile_id': created_profiles[0].id,
            'product_id': 'product_2'
        }
    ]

    # Clear existing wishlist items
    for profile in created_profiles:
        WishlistItem.query.filter_by(profile_id=profile.id).delete()

    for item_data in wishlist_items:
        item = WishlistItem(**item_data)
        db.session.add(item)
    db.session.commit()
    print("Updated wishlist items")

    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_data()