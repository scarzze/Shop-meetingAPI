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

def seed_database():
    print("🌱 Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    WishlistItem.query.delete()
    Profile.query.delete()
    db.session.commit()
    
    # Create test profiles
    print("Creating profiles...")
    profiles = [
        Profile(
            user_id="test_user_1",
            name="Test User 1",
            avatar="https://example.com/avatar1.jpg",
            preferences={"theme": "dark", "notifications": True}
        ),
        Profile(
            user_id="test_user_2",
            name="Test User 2",
            avatar="https://example.com/avatar2.jpg",
            preferences={"theme": "light", "notifications": False}
        )
    ]
    
    for profile in profiles:
        db.session.add(profile)
    db.session.commit()
    
    # Add wishlist items
    print("Creating wishlist items...")
    # Using sample product IDs that match the format in your routes
    test_products = ['prod_001', 'prod_002', 'prod_003', 'prod_004']
    
    for profile in profiles:
        # Add 2 products to each profile's wishlist
        items = [
            WishlistItem(
                profile_id=profile.id,
                product_id=test_products[0],
            ),
            WishlistItem(
                profile_id=profile.id,
                product_id=test_products[1],
            )
        ]
        db.session.add_all(items)
    
    db.session.commit()
    print("✅ Database seeding completed!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
