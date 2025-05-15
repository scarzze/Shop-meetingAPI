#!/usr/bin/env python
"""
Direct database seed script for Product Service
"""
import os
import sys
import json
import random
import sqlite3
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('product_seeder')

# Path to the SQLite database file
DB_PATH = 'services/product-service/instance/product_service.db'

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

def seed_categories(conn, cursor):
    """Seed categories into the database"""
    logger.info("Seeding categories...")
    
    # Check if categories table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='category'")
    if not cursor.fetchone():
        logger.warning("Categories table doesn't exist. Creating it...")
        cursor.execute("""
        CREATE TABLE category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    
    # Insert categories
    for category in categories:
        try:
            cursor.execute("""
            INSERT INTO category (name, description)
            VALUES (?, ?)
            """, (category["name"], category["description"]))
            logger.info(f"Added category: {category['name']}")
        except sqlite3.IntegrityError:
            logger.warning(f"Category '{category['name']}' already exists")
    
    conn.commit()

def seed_products(conn, cursor):
    """Seed products into the database"""
    logger.info("Seeding products...")
    
    # First, check if any products already exist
    cursor.execute("SELECT COUNT(*) FROM product")
    product_count = cursor.fetchone()[0]
    if product_count > 0:
        logger.info(f"Database already has {product_count} products. Skipping seeding.")
        return
    
    # Check if products table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product'")
    if not cursor.fetchone():
        logger.warning("Products table doesn't exist. Creating it...")
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
    
    # Insert products
    for product in products:
        try:
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
        except sqlite3.IntegrityError as e:
            logger.warning(f"Failed to add product '{product['name']}': {e}")
    
    conn.commit()

def main():
    """Main function to seed the database"""
    logger.info("Starting direct product database seeding")
    
    # Check if the database file exists
    if not os.path.isfile(DB_PATH):
        logger.error(f"Database file not found at {DB_PATH}")
        logger.info("Make sure the Product Service has been started at least once to create the database")
        sys.exit(1)
    
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Seed categories and products
        seed_categories(conn, cursor)
        seed_products(conn, cursor)
        
        # Close connection
        conn.close()
        
        logger.info("Product database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
