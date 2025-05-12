#!/usr/bin/env python3
"""
Seed script for Shop Meeting API services
This script populates the databases for each service with initial test data
"""

import requests
import json
import time
import random

# Base URLs for services
AUTH_SERVICE = "http://localhost:5002"
CART_SERVICE = "http://localhost:5001"
PRODUCT_SERVICE = "http://localhost:5006"
PROFILE_SERVICE = "http://localhost:5003"
ORDER_SERVICE = "http://localhost:5005"
SUPPORT_SERVICE = "http://localhost:5004"

# Sample data
users = [
    {"email": "admin@shop.com", "password": "Admin123!", "first_name": "Admin", "last_name": "User", "is_admin": True},
    {"email": "john@example.com", "password": "Password123!", "first_name": "John", "last_name": "Doe"},
    {"email": "jane@example.com", "password": "Password123!", "first_name": "Jane", "last_name": "Smith"},
    {"email": "customer@shop.com", "password": "Customer123!", "first_name": "Regular", "last_name": "Customer"}
]

products = [
    {
        "name": "Smartphone X", 
        "price": 799.99, 
        "description": "Latest smartphone with 6.5 inch display and 128GB storage",
        "category": "electronics",
        "image_url": "https://example.com/smartphone-x.jpg",
        "stock": 50
    },
    {
        "name": "Laptop Pro", 
        "price": 1299.99, 
        "description": "Powerful laptop with 16GB RAM and 512GB SSD",
        "category": "electronics",
        "image_url": "https://example.com/laptop-pro.jpg",
        "stock": 25
    },
    {
        "name": "Wireless Headphones", 
        "price": 129.99, 
        "description": "Noise-cancelling wireless headphones with 20 hour battery life",
        "category": "electronics",
        "image_url": "https://example.com/headphones.jpg",
        "stock": 100
    },
    {
        "name": "Running Shoes", 
        "price": 89.99, 
        "description": "Comfortable running shoes for all terrains",
        "category": "clothing",
        "image_url": "https://example.com/shoes.jpg",
        "stock": 75
    },
    {
        "name": "Winter Jacket", 
        "price": 149.99, 
        "description": "Warm winter jacket with water-resistant outer layer",
        "category": "clothing",
        "image_url": "https://example.com/jacket.jpg",
        "stock": 40
    }
]

addresses = [
    {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "USA",
        "is_default": True
    },
    {
        "street": "456 Oak Ave",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94107",
        "country": "USA",
        "is_default": False
    }
]

# Token storage
tokens = {}

def seed_auth_service():
    """Seed authentication service with users"""
    print("\n=== Seeding Auth Service ===")
    registered_users = []
    
    # From code inspection, we know the exact required fields
    print("Using exact required fields for auth registration")
    
    for user in users:
        try:
            # Use the exact required fields from the auth service code
            payload = {
                "email": user["email"],
                "password": user["password"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
            
            # Check if user is admin
            if user.get("is_admin", False):
                payload["is_admin"] = True
                
            response = requests.post(f"{AUTH_SERVICE}/auth/register", json=payload)
            
            if response.status_code == 201 or response.status_code == 200:
                print(f"Created user: {user['email']}")
                registered_users.append(user)
                
                # Login to get token - attempt both email and username
                login_payload = {"password": user["password"]}
                # Try email first
                login_payload["email"] = user["email"]
                login_response = requests.post(f"{AUTH_SERVICE}/auth/login", json=login_payload)
                
                # If that fails, try username
                if login_response.status_code != 200:
                    login_payload = {"username": user["name"], "password": user["password"]}
                    login_response = requests.post(f"{AUTH_SERVICE}/auth/login", json=login_payload)
                
                if login_response.status_code == 200:
                    tokens[user["email"]] = login_response.json().get("token")
                    print(f"Got token for {user['email']}")
            else:
                print(f"Failed to create user {user['email']}: {response.text}")
        except Exception as e:
            print(f"Error creating user {user['email']}: {str(e)}")
    
    return registered_users

def seed_product_service():
    """Seed product service with products"""
    print("\n=== Seeding Product Service ===")
    created_products = []
    
    # Get admin token
    admin_token = tokens.get("admin@shop.com")
    
    for product in products:
        try:
            headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
            
            # Use the /api/products endpoint from the service check response
            response = requests.post(f"{PRODUCT_SERVICE}/api/products", 
                                   json=product,
                                   headers=headers)
            
            if response.status_code == 201 or response.status_code == 200:
                created_product = response.json()
                created_products.append(created_product)
                print(f"Created product: {product['name']}")
            else:
                print(f"Failed to create product {product['name']}: {response.text}")
        except Exception as e:
            print(f"Error creating product {product['name']}: {str(e)}")
    
    return created_products

def seed_profile_service(registered_users):
    """Seed profile service with user profiles and addresses"""
    print("\n=== Seeding Profile Service ===")
    created_profiles = []
    
    # Check profile service endpoints first
    try:
        profile_info = requests.get(f"{PROFILE_SERVICE}")
        print(f"Profile service info: {profile_info.status_code} - {profile_info.text[:100]}")
    except Exception as e:
        print(f"Error getting profile info: {str(e)}")
    
    for user in registered_users:
        try:
            # Add profile information
            token = tokens.get(user["email"])
            if not token:
                print(f"No token for {user['email']}, skipping profile creation")
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            profile_data = {
                "phone": f"+1{random.randint(2000000000, 9999999999)}",
                "bio": f"This is the bio for {user['name']}"
            }
            
            # Use the correct profile endpoint from service response
            response = requests.patch(f"{PROFILE_SERVICE}/profile", 
                                    json=profile_data,
                                    headers=headers)
            
            if response.status_code == 200:
                print(f"Updated profile for: {user['email']}")
                
                # Add addresses
                for address in addresses:
                    addr_response = requests.post(f"{PROFILE_SERVICE}/addresses", 
                                               json=address,
                                               headers=headers)
                    
                    if addr_response.status_code == 201 or addr_response.status_code == 200:
                        print(f"Added address for {user['email']}")
                    else:
                        print(f"Failed to add address for {user['email']}: {addr_response.text}")
                
                created_profiles.append(user)
            else:
                print(f"Failed to update profile for {user['email']}: {response.text}")
        except Exception as e:
            print(f"Error creating profile for {user['email']}: {str(e)}")
    
    return created_profiles

def seed_cart_service(registered_users, created_products):
    """Seed cart service with items in users' carts"""
    print("\n=== Seeding Cart Service ===")
    
    # Check cart service endpoints first
    try:
        cart_info = requests.get(f"{CART_SERVICE}")
        print(f"Cart service info: {cart_info.status_code} - {cart_info.text[:100]}")
    except Exception as e:
        print(f"Error getting cart info: {str(e)}")
    
    for user in registered_users:
        try:
            token = tokens.get(user["email"])
            if not token:
                print(f"No token for {user['email']}, skipping cart creation")
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test with 1 product first to see if the API works
            if created_products:
                print(f"Testing cart API with one product")
                product = created_products[0]
                product_id = product.get("id") or product.get("product_id")
                if product_id:
                    cart_item = {
                        "product_id": product_id,
                        "quantity": 1
                    }
                    
                    # Try both endpoints
                    response = requests.post(f"{CART_SERVICE}/", 
                                           json=cart_item,
                                           headers=headers)
                    print(f"Cart add response: {response.status_code} - {response.text[:100]}")
                    
                    # If first attempt failed, try with different endpoint
                    if response.status_code >= 400:
                        response = requests.post(f"{CART_SERVICE}/cart", 
                                               json=cart_item,
                                               headers=headers)
                        print(f"Cart add (alt endpoint) response: {response.status_code} - {response.text[:100]}")
                    
                    # Only continue if we have a successful response
                    if response.status_code < 400:
                        # Add 1-3 random products to cart
                        num_products = min(len(created_products), random.randint(1, 3))
                        random_products = random.sample(created_products, num_products)
                        
                        for product in random_products:
                            product_id = product.get("id") or product.get("product_id")
                            if not product_id:
                                continue
                                
                            cart_item = {
                                "product_id": product_id,
                                "quantity": random.randint(1, 3)
                            }
                            
                            response = requests.post(f"{CART_SERVICE}/", 
                                                   json=cart_item,
                                                   headers=headers)
                
                if response.status_code == 201 or response.status_code == 200:
                    print(f"Added product {product_id} to cart for {user['email']}")
                else:
                    print(f"Failed to add product to cart for {user['email']}: {response.text}")
        except Exception as e:
            print(f"Error adding to cart for {user['email']}: {str(e)}")

def create_orders(registered_users):
    """Create orders for some users"""
    print("\n=== Creating Orders ===")
    
    for user in registered_users:
        # 50% chance to create an order for this user
        if random.random() < 0.5:
            continue
            
        try:
            token = tokens.get(user["email"])
            if not token:
                print(f"No token for {user['email']}, skipping order creation")
                continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get cart
            cart_response = requests.get(f"{CART_SERVICE}/", headers=headers)
            
            if cart_response.status_code != 200:
                print(f"Failed to get cart for {user['email']}, skipping order")
                continue
                
            cart = cart_response.json()
            cart_id = cart.get("cart_id")
            
            if not cart_id:
                print(f"No cart ID found for {user['email']}, skipping order")
                continue
            
            # Create order from cart
            order_data = {
                "cart_id": cart_id,
                "shipping_address_id": 1  # Assuming first address is default
            }
            
            order_response = requests.post(f"{ORDER_SERVICE}/orders", 
                                         json=order_data,
                                         headers=headers)
            
            if order_response.status_code == 201 or order_response.status_code == 200:
                print(f"Created order for {user['email']}")
            else:
                print(f"Failed to create order for {user['email']}: {order_response.text}")
        except Exception as e:
            print(f"Error creating order for {user['email']}: {str(e)}")

def check_service_endpoints():
    """Check which endpoints are available on each service"""
    print("\n=== Checking Service Endpoints ===")
    
    # Check Auth Service
    try:
        auth_response = requests.get(f"{AUTH_SERVICE}/health")
        print(f"Auth Service: {auth_response.status_code} - {auth_response.text[:100]}")
    except Exception as e:
        print(f"Auth Service Error: {str(e)}")

    # Check Cart Service
    try:
        cart_response = requests.get(f"{CART_SERVICE}/health")
        print(f"Cart Service: {cart_response.status_code} - {cart_response.text[:100]}")
    except Exception as e:
        print(f"Cart Service Error: {str(e)}")
    
    # Check Product Service
    try:
        product_response = requests.get(f"{PRODUCT_SERVICE}")
        print(f"Product Service: {product_response.status_code} - {product_response.text[:100]}")
    except Exception as e:
        print(f"Product Service Error: {str(e)}")

    # Check Profile Service
    try:
        profile_response = requests.get(f"{PROFILE_SERVICE}")
        print(f"Profile Service: {profile_response.status_code} - {profile_response.text[:100]}")
    except Exception as e:
        print(f"Profile Service Error: {str(e)}")
    
    # Check Order Service
    try:
        order_response = requests.get(f"{ORDER_SERVICE}/health")
        print(f"Order Service: {order_response.status_code} - {order_response.text[:100]}")
    except Exception as e:
        print(f"Order Service Error: {str(e)}")

def main():
    """Main function to seed all services"""
    print("Starting data seeding process for Shop Meeting API...")
    
    try:
        # First check which endpoints are actually available
        check_service_endpoints()
        
        print("\nDo you want to continue with seeding? (y/n)")
        choice = input()
        if choice.lower() != 'y':
            print("Seeding cancelled.")
            return
            
        # Seed auth service first to get tokens
        registered_users = seed_auth_service()
        
        # Allow time for user propagation
        print("Waiting for user data propagation...")
        time.sleep(2)
        
        # Seed products
        created_products = seed_product_service()
        
        # Seed profiles
        seed_profile_service(registered_users)
        
        # Seed carts with items
        seed_cart_service(registered_users, created_products)
        
        # Create some orders
        create_orders(registered_users)
        
        print("\n=== Seeding Complete ===")
        print("Test users created:")
        for user in users:
            print(f"  - Email: {user['email']}, Password: {user['password']}")
        
    except Exception as e:
        print(f"Error during seeding process: {str(e)}")

if __name__ == "__main__":
    main()
