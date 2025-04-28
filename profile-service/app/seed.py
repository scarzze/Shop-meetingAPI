"""
Database seeder for the Profile Service

This script populates the database with sample data for testing and development.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import random
from app import create_app, db
from app.models import Profile, WishlistItem

# Sample user data
USERS = [
    {
        'user_id': 'user_01',
        'name': 'John Doe',
        'avatar': 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg',
        'preferences': {
            'theme': 'light',
            'notifications': True,
            'categories': ['electronics', 'books', 'fashion']
        }
    },
    {
        'user_id': 'user_02',
        'name': 'Jane Smith',
        'avatar': 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg',
        'preferences': {
            'theme': 'dark',
            'notifications': True,
            'categories': ['home', 'beauty', 'sports']
        }
    },
    {
        'user_id': 'user_03',
        'name': 'Alex Johnson',
        'avatar': 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg',
        'preferences': {
            'theme': 'system',
            'notifications': False,
            'categories': ['gaming', 'music', 'tech']
        }
    }
]

# Sample product IDs (these should match existing products in your product service)
PRODUCT_IDS = [
    'prod_001', 'prod_002', 'prod_003', 'prod_004', 
    'prod_005', 'prod_006', 'prod_007', 'prod_008'
]

def seed_database():
    """Seed the database with sample data"""
    
    print("🌱 Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    WishlistItem.query.delete()
    Profile.query.delete()
    db.session.commit()
    
    # Create profiles
    print("Creating profiles...")
    profiles = []
    base_date = datetime.utcnow() - timedelta(days=30)
    
    for user_data in USERS:
        profile = Profile(
            user_id=user_data['user_id'],
            name=user_data['name'],
            avatar=user_data['avatar'],
            preferences=user_data['preferences'],
            created_at=base_date + timedelta(days=random.randint(0, 15)),
            updated_at=base_date + timedelta(days=random.randint(16, 30))
        )
        db.session.add(profile)
        profiles.append(profile)
    
    db.session.commit()
    print(f"Created {len(profiles)} profiles")
    
    # Add wishlist items
    print("Creating wishlist items...")
    wishlist_count = 0
    
    for profile in profiles:
        # Randomly select 2-4 products for each profile
        num_products = random.randint(2, 4)
        selected_products = random.sample(PRODUCT_IDS, num_products)
        
        for product_id in selected_products:
            wishlist_item = WishlistItem(
                profile_id=profile.id,
                product_id=product_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.session.add(wishlist_item)
            wishlist_count += 1
    
    db.session.commit()
    print(f"Created {wishlist_count} wishlist items")
    
    print("✅ Database seeding completed!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
