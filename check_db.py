import sqlite3
import json

# Path to the SQLite database file
DB_PATH = 'services/product-service/instance/product_service.db'

def main():
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dictionary access by column name
    cursor = conn.cursor()
    
    # Query categories
    print("\nCategories:")
    cursor.execute("SELECT * FROM category")
    categories = [dict(row) for row in cursor.fetchall()]
    for category in categories:
        print(f"ID: {category['id']}, Name: {category['name']}")
    
    # Query products
    print("\nProducts:")
    cursor.execute("""
    SELECT p.id, p.name, p.price, p.stock_quantity, p.category_id, c.name as category_name 
    FROM product p 
    LEFT JOIN category c ON p.category_id = c.id
    """)
    products = [dict(row) for row in cursor.fetchall()]
    for product in products:
        print(f"ID: {product['id']}, Name: {product['name']}, Price: ${product['price']}, Category: {product['category_name']}")
    
    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
