#!/usr/bin/env python
"""
Fix Product Service database and seed products
"""
import os
import sys
import random
import sqlite3
import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('product_db_fixer')

# Make sure instance directory exists
INSTANCE_DIR = 'services/product-service/instance'
DB_PATH = f'{INSTANCE_DIR}/product_service.db'

# Sample categories
categories = [
    {"name": "Electronics", "description": "Electronic devices and gadgets"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Home & Kitchen", "description": "Household and kitchen products"},
    {"name": "Books", "description": "Books and publications"}
]

# Sample products
products = [
    {
        "name": "Ultra HD Smart TV",
        "description": "75-inch 4K Ultra HD Smart TV with Alexa compatibility",
        "price": 1299.99,
        "stock_quantity": 25,
        "category_id": 1,  # Electronics
        "image_url": "https://example.com/images/tv.jpg"
    },
    {
        "name": "Wireless Noise-Cancelling Headphones",
        "description": "Premium wireless headphones with active noise cancellation",
        "price": 349.99,
        "stock_quantity": 50,
        "category_id": 1,  # Electronics
        "image_url": "https://example.com/images/headphones.jpg"
    },
    {
        "name": "Premium Cotton T-Shirt",
        "description": "Comfortable 100% cotton t-shirt in various colors",
        "price": 29.99,
        "stock_quantity": 100,
        "category_id": 2,  # Clothing
        "image_url": "https://example.com/images/tshirt.jpg"
    },
    {
        "name": "Designer Denim Jeans",
        "description": "High-quality denim jeans with modern fit",
        "price": 89.99,
        "stock_quantity": 75,
        "category_id": 2,  # Clothing
        "image_url": "https://example.com/images/jeans.jpg"
    },
    {
        "name": "Smart Coffee Maker",
        "description": "Programmable coffee maker with smartphone controls",
        "price": 129.99,
        "stock_quantity": 30,
        "category_id": 3,  # Home & Kitchen
        "image_url": "https://example.com/images/coffeemaker.jpg"
    },
    {
        "name": "Non-Stick Cookware Set",
        "description": "12-piece non-stick cookware set with glass lids",
        "price": 199.99,
        "stock_quantity": 20,
        "category_id": 3,  # Home & Kitchen
        "image_url": "https://example.com/images/cookware.jpg"
    },
    {
        "name": "Best-Selling Novel",
        "description": "Award-winning fiction novel by renowned author",
        "price": 24.99,
        "stock_quantity": 150,
        "category_id": 4,  # Books
        "image_url": "https://example.com/images/novel.jpg"
    },
    {
        "name": "Programming Handbook",
        "description": "Comprehensive guide to modern programming languages",
        "price": 59.99,
        "stock_quantity": 40,
        "category_id": 4,  # Books
        "image_url": "https://example.com/images/programming.jpg"
    }
]

def ensure_dir_exists(dir_path):
    """Ensure directory exists"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def main():
    """Main function to recreate and seed the database"""
    logger.info("Starting product database fix and seeding")
    
    # Ensure instance directory exists
    ensure_dir_exists(INSTANCE_DIR)
    logger.info(f"Instance directory ensured at {INSTANCE_DIR}")
    
    # Remove existing database if it exists (start fresh)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info(f"Removed existing database at {DB_PATH}")
    
    try:
        # Connect to the database (will create a new file)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        logger.info(f"Connected to database at {DB_PATH}")
        
        # Create tables
        logger.info("Creating database tables...")
        
        # Create category table
        cursor.execute("""
        CREATE TABLE category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create product table
        cursor.execute("""
        CREATE TABLE product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            category_id INTEGER,
            image_url TEXT,
            sku TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES category (id)
        )
        """)
        
        # Create review table
        cursor.execute("""
        CREATE TABLE review (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            user_name TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES product (id) ON DELETE CASCADE
        )
        """)
        
        # Seed categories
        logger.info("Seeding categories...")
        for category in categories:
            cursor.execute("""
            INSERT INTO category (name, description)
            VALUES (?, ?)
            """, (category["name"], category["description"]))
            logger.info(f"Added category: {category['name']}")
        
        # Seed products
        logger.info("Seeding products...")
        for product in products:
            # Generate a unique SKU
            sku = f"SKU-{random.randint(10000, 99999)}"
            
            cursor.execute("""
            INSERT INTO product (name, description, price, stock_quantity, category_id, sku, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                product["name"],
                product["description"],
                product["price"],
                product["stock_quantity"],
                product["category_id"],
                sku,
                product["image_url"]
            ))
            logger.info(f"Added product: {product['name']}")
        
        # Add some sample reviews for products
        logger.info("Adding sample product reviews...")
        sample_users = [
            {"id": "user1", "name": "John Doe"},
            {"id": "user2", "name": "Jane Smith"},
            {"id": "user3", "name": "Robert Jones"}
        ]
        
        for product_id in range(1, len(products) + 1):
            # Add 2-3 reviews per product
            num_reviews = random.randint(2, 3)
            for _ in range(num_reviews):
                user = random.choice(sample_users)
                rating = random.randint(3, 5)  # Random rating between 3-5
                comment = "This product is great!" if rating >= 4 else "Decent product, but could be better."
                
                cursor.execute("""
                INSERT INTO review (product_id, user_id, user_name, rating, comment)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    product_id,
                    user["id"],
                    user["name"],
                    rating,
                    comment
                ))
        
        # Commit all changes
        conn.commit()
        
        # Verify data was inserted correctly
        cursor.execute("SELECT COUNT(*) FROM category")
        category_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM product")
        product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM review")
        review_count = cursor.fetchone()[0]
        
        logger.info(f"Database seeding completed successfully!")
        logger.info(f"Added {category_count} categories, {product_count} products, and {review_count} reviews")
        
        # Close connection
        conn.close()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Error creating/seeding database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
