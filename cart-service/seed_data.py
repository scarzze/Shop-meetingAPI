import os
from app import app
from models import db, Product

def seed_products():
    """Seed the database with sample products"""
    
    # Products to be added
    products = [
        {
            'id': 1,
            'name': 'Laptop',
            'description': 'High-performance laptop with 16GB RAM and 512GB SSD',
            'price': 26000.00,
            'image_url': 'https://example.com/images/laptop.jpg',
            'category': 'Electronics'
        },
        {
            'id': 2,
            'name': 'Smartphone',
            'description': 'Latest smartphone with 6.5-inch display and 128GB storage',
            'price': 15000.00,
            'image_url': 'https://example.com/images/smartphone.jpg',
            'category': 'Electronics'
        },
        {
            'id': 3,
            'name': 'Headphones',
            'description': 'Noise-cancelling wireless headphones',
            'price': 5000.00,
            'image_url': 'https://example.com/images/headphones.jpg',
            'category': 'Electronics'
        },
        {
            'id': 4,
            'name': 'Coffee Maker',
            'description': 'Programmable coffee maker with thermal carafe',
            'price': 3500.00,
            'image_url': 'https://example.com/images/coffeemaker.jpg',
            'category': 'Home Appliances'
        },
        {
            'id': 5,
            'name': 'Running Shoes',
            'description': 'Lightweight running shoes with cushioned sole',
            'price': 2800.00,
            'image_url': 'https://example.com/images/runningshoes.jpg',
            'category': 'Footwear'
        }
    ]
    
    # Check if products already exist
    existing_products = Product.query.all()
    if existing_products:
        print(f"{len(existing_products)} products already exist in the database.")
        return False
    
    # Add products to database
    for product_data in products:
        product = Product(**product_data)
        db.session.add(product)
    
    db.session.commit()
    print(f"Added {len(products)} products to the database.")
    return True

if __name__ == "__main__":
    with app.app_context():
        seed_products()
