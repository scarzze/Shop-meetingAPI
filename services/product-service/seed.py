"""
Seed script to populate the database with initial test data
"""
from app import create_app
from app.models import db, Category, Product, Review
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_categories():
    """Seed categories into the database"""
    logger.info("Seeding categories...")
    
    categories = [
        {"name": "Electronics", "description": "Electronic devices and gadgets"},
        {"name": "Clothing", "description": "Apparel and fashion items"},
        {"name": "Books", "description": "Books, e-books, and literature"},
        {"name": "Home & Kitchen", "description": "Home decor and kitchen appliances"},
        {"name": "Sports & Outdoors", "description": "Sports equipment and outdoor gear"}
    ]
    
    category_objects = []
    for category_data in categories:
        # Check if category already exists
        existing = Category.query.filter_by(name=category_data["name"]).first()
        if existing:
            logger.info(f"Category '{category_data['name']}' already exists, skipping.")
            category_objects.append(existing)
            continue
            
        category = Category(**category_data)
        db.session.add(category)
        category_objects.append(category)
        logger.info(f"Added category: {category_data['name']}")
        
    db.session.commit()
    return category_objects

def seed_products(categories):
    """Seed products into the database"""
    logger.info("Seeding products...")
    
    products = [
        {
            "name": "Smartphone",
            "description": "Latest model smartphone with high-resolution camera",
            "price": 999.99,
            "category_id": categories[0].id,  # Electronics
            "stock_quantity": 50,
            "sku": "PHONE-001",
            "image_url": "http://example.com/images/phone.jpg"
        },
        {
            "name": "Laptop",
            "description": "Powerful laptop for work and gaming",
            "price": 1299.99,
            "category_id": categories[0].id,  # Electronics
            "stock_quantity": 25,
            "sku": "LAPTOP-001",
            "image_url": "http://example.com/images/laptop.jpg"
        },
        {
            "name": "T-Shirt",
            "description": "Comfortable cotton t-shirt",
            "price": 19.99,
            "category_id": categories[1].id,  # Clothing
            "stock_quantity": 100,
            "sku": "TSHIRT-001",
            "image_url": "http://example.com/images/tshirt.jpg"
        },
        {
            "name": "Jeans",
            "description": "Classic blue jeans",
            "price": 49.99,
            "category_id": categories[1].id,  # Clothing
            "stock_quantity": 75,
            "sku": "JEANS-001",
            "image_url": "http://example.com/images/jeans.jpg"
        },
        {
            "name": "Science Fiction Novel",
            "description": "Bestselling sci-fi novel",
            "price": 14.99,
            "category_id": categories[2].id,  # Books
            "stock_quantity": 200,
            "sku": "BOOK-001",
            "image_url": "http://example.com/images/book.jpg"
        },
        {
            "name": "Cookbook",
            "description": "Recipes from around the world",
            "price": 24.99,
            "category_id": categories[2].id,  # Books
            "stock_quantity": 150,
            "sku": "BOOK-002",
            "image_url": "http://example.com/images/cookbook.jpg"
        },
        {
            "name": "Coffee Maker",
            "description": "Automatic coffee maker with timer",
            "price": 79.99,
            "category_id": categories[3].id,  # Home & Kitchen
            "stock_quantity": 40,
            "sku": "COFFEE-001",
            "image_url": "http://example.com/images/coffeemaker.jpg"
        },
        {
            "name": "Bed Sheets",
            "description": "100% cotton bed sheets, queen size",
            "price": 39.99,
            "category_id": categories[3].id,  # Home & Kitchen
            "stock_quantity": 60,
            "sku": "SHEETS-001",
            "image_url": "http://example.com/images/sheets.jpg"
        },
        {
            "name": "Basketball",
            "description": "Official size basketball",
            "price": 29.99,
            "category_id": categories[4].id,  # Sports & Outdoors
            "stock_quantity": 80,
            "sku": "SPORT-001",
            "image_url": "http://example.com/images/basketball.jpg"
        },
        {
            "name": "Tent",
            "description": "4-person camping tent",
            "price": 129.99,
            "category_id": categories[4].id,  # Sports & Outdoors
            "stock_quantity": 30,
            "sku": "CAMP-001",
            "image_url": "http://example.com/images/tent.jpg"
        }
    ]
    
    product_objects = []
    for product_data in products:
        # Check if product already exists
        existing = Product.query.filter_by(sku=product_data["sku"]).first()
        if existing:
            logger.info(f"Product with SKU '{product_data['sku']}' already exists, skipping.")
            product_objects.append(existing)
            continue
            
        product = Product(**product_data)
        db.session.add(product)
        product_objects.append(product)
        logger.info(f"Added product: {product_data['name']}")
        
    db.session.commit()
    return product_objects

def seed_reviews(products):
    """Seed reviews into the database"""
    logger.info("Seeding reviews...")
    
    reviews = [
        {
            "product_id": products[0].id,  # Smartphone
            "user_id": "user-001",
            "user_name": "John Doe",
            "rating": 5,
            "comment": "Great smartphone! The camera is amazing."
        },
        {
            "product_id": products[0].id,  # Smartphone
            "user_id": "user-002",
            "user_name": "Jane Smith",
            "rating": 4,
            "comment": "Good phone, but battery life could be better."
        },
        {
            "product_id": products[1].id,  # Laptop
            "user_id": "user-001",
            "user_name": "John Doe",
            "rating": 5,
            "comment": "Powerful laptop, perfect for gaming and work."
        },
        {
            "product_id": products[2].id,  # T-Shirt
            "user_id": "user-003",
            "user_name": "Bob Johnson",
            "rating": 3,
            "comment": "Average quality, but comfortable."
        },
        {
            "product_id": products[4].id,  # Science Fiction Novel
            "user_id": "user-002",
            "user_name": "Jane Smith",
            "rating": 5,
            "comment": "Couldn't put it down! Amazing story."
        }
    ]
    
    for review_data in reviews:
        # Check if review already exists
        existing = Review.query.filter_by(
            product_id=review_data["product_id"],
            user_id=review_data["user_id"]
        ).first()
        
        if existing:
            logger.info(f"Review by user {review_data['user_id']} for product {review_data['product_id']} already exists, skipping.")
            continue
            
        review = Review(**review_data)
        db.session.add(review)
        logger.info(f"Added review for product ID {review_data['product_id']} by {review_data['user_name']}")
        
    db.session.commit()

def main():
    """Main function to seed the database"""
    app = create_app()
    with app.app_context():
        logger.info("Starting database seeding...")
        # Create all tables if they don't exist
        db.create_all()
        
        # Seed data
        categories = seed_categories()
        products = seed_products(categories)
        seed_reviews(products)
        
        logger.info("Database seeding completed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
