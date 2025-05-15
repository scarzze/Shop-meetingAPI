#!/usr/bin/env python
"""
Seed data script for Shop-meetingAPI
This script populates the databases with sample data for testing and development.
"""
import os
import sys
import json
import random
import requests
import datetime

# Base URLs for services
AUTH_SERVICE_URL = "http://localhost:5002"
PROFILE_SERVICE_URL = "http://localhost:5003"
PRODUCT_SERVICE_URL = "http://localhost:5006"
CART_SERVICE_URL = "http://localhost:5001"
ORDER_SERVICE_URL = "http://localhost:5005"
CUSTOMER_SUPPORT_URL = "http://localhost:5004"

# Sample user data
users = [
    {
        "email": "john.doe@gmail.com", 
        "password": "Password123", 
        "first_name": "John", 
        "last_name": "Doe"
    },
    {
        "email": "jane.doe@gmail.com", 
        "password": "Password123", 
        "first_name": "Jane", 
        "last_name": "Doe"
    },
    {
        "email": "bob.smith@gmail.com", 
        "password": "Password123", 
        "first_name": "Bob", 
        "last_name": "Smith"
    },
]

# Sample product data
products = [
    {
        "name": "Smartphone X",
        "description": "Latest smartphone with advanced features",
        "price": 999.99,
        "category_id": 1,  # Using ID instead of name
        "sku": "PHONE-X-001",
        "image_url": "https://example.com/smartphone.jpg",
        "stock_quantity": 50,
        "weight": 0.3,  # in kg
        "dimensions": {"length": 15, "width": 7, "height": 1}  # in cm
    },
    {
        "name": "Laptop Pro",
        "description": "High-performance laptop for professionals",
        "price": 1499.99,
        "category_id": 1,  # Using ID instead of name
        "sku": "LAPTOP-PRO-001",
        "image_url": "https://example.com/laptop.jpg",
        "stock_quantity": 30,
        "weight": 2.1,  # in kg
        "dimensions": {"length": 35, "width": 25, "height": 2}  # in cm
    },
    {
        "name": "Wireless Earbuds",
        "description": "Premium sound quality with noise cancellation",
        "price": 199.99,
        "category_id": 2,  # Using ID instead of name
        "sku": "EARBUDS-001",
        "image_url": "https://example.com/earbuds.jpg",
        "stock_quantity": 100,
        "weight": 0.05,  # in kg
        "dimensions": {"length": 5, "width": 5, "height": 2}  # in cm
    },
    {
        "name": "Smart Watch",
        "description": "Track your fitness and stay connected",
        "price": 299.99,
        "category_id": 3,  # Using ID instead of name
        "sku": "WATCH-001",
        "image_url": "https://example.com/smartwatch.jpg",
        "stock_quantity": 75,
        "weight": 0.08,  # in kg
        "dimensions": {"length": 4, "width": 4, "height": 1}  # in cm
    },
    {
        "name": "Coffee Maker",
        "description": "Brew perfect coffee every morning",
        "price": 89.99,
        "category_id": 4,  # Using ID instead of name
        "sku": "COFFEE-001",
        "image_url": "https://example.com/coffeemaker.jpg",
        "stock_quantity": 60,
        "weight": 2.5,  # in kg
        "dimensions": {"length": 30, "width": 20, "height": 40}  # in cm
    }
]

# Sample profile data - will be associated with users after creation
profiles = [
    {
        "name": "John Doe",
        "email": "john.doe@gmail.com",
        "phone_number": "+1234567890",
        "address": "123 Main St, New York, NY 10001"
    },
    {
        "name": "Jane Doe",
        "email": "jane.doe@gmail.com",
        "phone_number": "+1987654321",
        "address": "456 Park Ave, Los Angeles, CA 90001"
    },
    {
        "name": "Bob Smith",
        "email": "bob.smith@gmail.com",
        "phone_number": "+1555123456",
        "address": "789 Oak Rd, Chicago, IL 60007"
    }
]

# Sample addresses - will be associated with users after creation
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
        "street": "456 Park Ave",
        "city": "Los Angeles",
        "state": "CA",
        "postal_code": "90001",
        "country": "USA",
        "is_default": True
    },
    {
        "street": "789 Oak Rd",
        "city": "Chicago",
        "state": "IL",
        "postal_code": "60007",
        "country": "USA",
        "is_default": True
    }
]

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_colored(message, color=Colors.GREEN):
    print(f"{color}{message}{Colors.RESET}")

def check_service_health(service_name, url):
    """Check if a service is healthy before proceeding"""
    try:
        response = requests.get(f"{url}/health")
        if response.status_code == 200:
            print_colored(f"[OK] {service_name} is healthy")
            return True
        else:
            print_colored(f"[ERROR] {service_name} returned status code {response.status_code}", Colors.RED)
            return False
    except requests.RequestException as e:
        print_colored(f"[ERROR] {service_name} is not reachable: {str(e)}", Colors.RED)
        return False

def register_users():
    """Register sample users with the Auth Service or login if they already exist"""
    print_colored("\nRegistering/logging in users...")
    registered_users = []
    
    for user in users:
        try:
            # Try to register the user first
            register_response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=user)
            
            # If registration succeeds or user already exists, try to log in
            login_response = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            
            if login_response.status_code == 200:
                # User logged in successfully
                login_data = login_response.json()
                user_data = login_data.get("user", {})
                
                registered_user = {
                    "id": user_data.get("id", 1),  # Use default ID if not provided
                    "username": f"{user['first_name']}_{user['last_name']}".lower(),
                    "email": user["email"],
                    "password": user["password"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "access_token": login_data.get("access_token", "")
                }
                registered_users.append(registered_user)
                print_colored(f"  [OK] User authenticated: {user['first_name']} {user['last_name']}")
            elif register_response.status_code == 200 or register_response.status_code == 201:
                # User was registered successfully but login failed
                data = register_response.json()
                registered_user = {
                    "id": data.get("user", {}).get("id", 1),
                    "username": f"{user['first_name']}_{user['last_name']}".lower(),
                    "email": user["email"],
                    "password": user["password"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"]
                }
                registered_users.append(registered_user)
                print_colored(f"  [OK] Registered user: {user['first_name']} {user['last_name']}")
            else:
                print_colored(f"  [ERROR] Failed to authenticate {user['first_name']} {user['last_name']}: {login_response.text}", Colors.YELLOW)
        except requests.RequestException as e:
            print_colored(f"  [ERROR] Error with user {user['first_name']} {user['last_name']}: {str(e)}", Colors.RED)
    
    return registered_users

def login_user(user):
    """Get token for a user, using stored token if available"""
    # If user already has a token from login, return it
    if "access_token" in user and user["access_token"]:
        return user["access_token"]
        
    # Otherwise try to log in
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print_colored(f"  [ERROR] Failed to login user {user['email']}: {response.text}", Colors.YELLOW)
            return None
    except requests.RequestException as e:
        print_colored(f"  [ERROR] Error logging in user {user['email']}: {str(e)}", Colors.RED)
        return None

def create_profiles(registered_users):
    """Create profiles for registered users"""
    print_colored("\nCreating user profiles...")
    
    for i, user in enumerate(registered_users):
        if i >= len(profiles):
            break
            
        # Login to get token
        token = login_user(user)
        if not token:
            continue
            
        # Create profile
        profile_data = profiles[i]
        try:
            # Create a simplified profile with required fields
            simplified_profile = {
                "name": f"{user['first_name']} {user['last_name']}",
                "email": user['email']
            }
            
            # Debug mode enabled - try both PUT and PATCH requests
            # First try PUT to create/replace the profile
            response = requests.put(
                f"{PROFILE_SERVICE_URL}/", 
                json=simplified_profile,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # If PUT fails, try PATCH to update existing profile
            if response.status_code >= 400:
                response = requests.patch(
                    f"{PROFILE_SERVICE_URL}/", 
                    json=simplified_profile,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
            if response.status_code == 200 or response.status_code == 201:
                print_colored(f"  ✅ Created/updated profile for: {user['first_name']} {user['last_name']}")
            else:
                print_colored(f"  ❌ Failed to create profile for {user['first_name']} {user['last_name']}: {response.text}", Colors.YELLOW)
        except requests.RequestException as e:
            print_colored(f"  ❌ Error creating profile for {user['first_name']} {user['last_name']}: {str(e)}", Colors.RED)
            
        # Try to add address information to the profile
        try:
            # First try updating the main profile with the address
            address_update = {
                "name": f"{user['first_name']} {user['last_name']}",
                "email": user['email'],
                "address": addresses[i]['street'] + ", " + addresses[i]['city'] + ", " + addresses[i]['state']
            }
            
            response = requests.patch(
                f"{PROFILE_SERVICE_URL}/", 
                json=address_update,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # As a fallback, try updating preferences if available
            if response.status_code >= 400:
                address_data = {"address": addresses[i]['street'] + ", " + addresses[i]['city'] + ", " + addresses[i]['state']}
                response = requests.patch(
                    f"{PROFILE_SERVICE_URL}/preferences", 
                    json=address_data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
            if response.status_code == 200 or response.status_code == 201:
                print_colored(f"  ✅ Added address for: {user['first_name']} {user['last_name']}")
            else:
                print_colored(f"  ❌ Failed to add address for {user['first_name']} {user['last_name']}: {response.text}", Colors.YELLOW)
        except requests.RequestException as e:
            print_colored(f"  ❌ Error adding address for {user['first_name']} {user['last_name']}: {str(e)}", Colors.RED)

def create_products():
    """Add sample products to the Product Service"""
    print_colored("\nCreating products...")
    
    # Get a token from a regular user (first user)
    if registered_users and len(registered_users) > 0:
        token = login_user(registered_users[0])
        if not token:
            print_colored("  [ERROR] Cannot create products without authentication", Colors.RED)
            return
    else:
        print_colored("  [ERROR] No registered users available for authentication", Colors.RED)
        return
    
    # First check if there are any categories, create if needed
    categories = [
        {"name": "Electronics", "description": "Electronic devices and gadgets"},
        {"name": "Clothing", "description": "Apparel and fashion items"},
        {"name": "Home & Kitchen", "description": "Household and kitchen products"},
        {"name": "Books", "description": "Books and publications"}
    ]
    
    # Create categories first
    for category in categories:
        try:
            response = requests.post(
                f"{PRODUCT_SERVICE_URL}/api/categories", 
                json=category,
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200 or response.status_code == 201:
                print_colored(f"  [OK] Created category {category['name']}")
            else:
                # Ignore if category already exists
                print_colored(f"  [INFO] Category {category['name']} may already exist: {response.text}", Colors.YELLOW)
        except requests.RequestException as e:
            print_colored(f"  [ERROR] Error creating category {category['name']}: {str(e)}", Colors.RED)
    
    # Try different product endpoints        
    for product in products:
        # Simplify product data to essential fields
        simplified_product = {
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "category_id": product.get("category_id", 1),  # Default to first category
            "stock_quantity": product.get("stock_quantity", 10)
        }
        
        try:
            # Try different endpoints
            endpoints = [
                "/api/products",
                "/products",
                "/product"
            ]
            
            success = False
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{PRODUCT_SERVICE_URL}{endpoint}", 
                        json=simplified_product,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if response.status_code == 200 or response.status_code == 201:
                        print_colored(f"  [OK] Created product {product['name']} via {endpoint}")
                        success = True
                        break
                except:
                    continue
            
            if not success:
                print_colored(f"  [ERROR] Failed to create product {product['name']}: Could not find working endpoint", Colors.YELLOW)
                
        except requests.RequestException as e:
            print_colored(f"  [ERROR] Error creating product {product['name']}: {str(e)}", Colors.RED)

def add_items_to_cart(registered_users):
    """Add items to user carts"""
    print_colored("\nAdding items to carts...")
    
    # First get product IDs (assuming they exist with IDs 1-5)
    product_ids = list(range(1, len(products) + 1))
    
    for user in registered_users:
        # Login to get token
        token = login_user(user)
        if not token:
            continue
            
        # Add random products to cart
        for _ in range(random.randint(1, 3)):
            product_id = random.choice(product_ids)
            quantity = random.randint(1, 2)
            
            # Try different cart endpoints and formats
            cart_endpoints = [
                {
                    "url": f"{CART_SERVICE_URL}/cart/add",
                    "data": {"product_id": product_id, "quantity": quantity}
                },
                {
                    "url": f"{CART_SERVICE_URL}/cart/items",
                    "data": {"product_id": product_id, "quantity": quantity}
                },
                {
                    "url": f"{CART_SERVICE_URL}/cart",
                    "data": {"item": {"product_id": product_id, "quantity": quantity}}
                }
            ]
            
            success = False
            for endpoint in cart_endpoints:
                try:
                    response = requests.post(
                        endpoint["url"], 
                        json=endpoint["data"],
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if response.status_code == 200 or response.status_code == 201:
                        print_colored(f"  ✅ Added product {product_id} to {user['first_name']}'s cart via {endpoint['url']}")
                        success = True
                        break
                except requests.RequestException:
                    continue
            
            if not success:
                print_colored(f"  ❌ Failed to add product {product_id} to cart: Could not find working endpoint", Colors.YELLOW)

def create_orders(registered_users):
    """Create orders for users"""
    print_colored("\nCreating orders...")
    
    for user in registered_users:
        # Login to get token
        token = login_user(user)
        if not token:
            continue
            
        # Create order with simplified data format based on API requirements
        order_data = {
            "user_id": user.get("id", 1),
            "items": [
                {"product_id": 1, "quantity": 1},
                {"product_id": 2, "quantity": 1}
            ],
            "shipping_details": {
                "name": f"{user['first_name']} {user['last_name']}",
                "address": "123 Main St, New York, NY 10001, USA",
                "phone": "+1234567890"
            },
            "payment_details": {
                "method": "credit_card",
                "card_number": "************1234",
                "expiry_date": "12/26",
                "card_holder": f"{user['first_name']} {user['last_name']}"
            }
        }
        
        # Try different order endpoints and formats
        order_endpoints = [
            {
                "url": f"{ORDER_SERVICE_URL}/orders",
                "data": order_data
            },
            {
                "url": f"{ORDER_SERVICE_URL}/order",
                "data": order_data
            },
            {
                "url": f"{ORDER_SERVICE_URL}/api/orders",
                "data": order_data
            },
            # Simpler format as fallback
            {
                "url": f"{ORDER_SERVICE_URL}/orders",
                "data": {
                    "user_id": user.get("id", 1),
                    "product_ids": [1, 2],
                    "shipping_address": "123 Main St, New York, NY 10001, USA",
                    "payment_method": "credit_card"
                }
            }
        ]
        
        success = False
        for endpoint in order_endpoints:
            try:
                response = requests.post(
                    endpoint["url"], 
                    json=endpoint["data"],
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200 or response.status_code == 201:
                    print_colored(f"  ✅ Created order for {user['first_name']} {user['last_name']} via {endpoint['url']}")
                    success = True
                    break
            except requests.RequestException:
                continue
        
        if not success:
            print_colored(f"  ❌ Failed to create order for {user['first_name']} {user['last_name']}: Could not find working endpoint", Colors.YELLOW)

def create_support_tickets(registered_users):
    """Create support tickets for users"""
    print_colored("\nCreating support tickets...")
    
    ticket_subjects = [
        "Question about my order",
        "Product information request",
        "Return policy inquiry",
        "Shipping delay"
    ]
    
    ticket_messages = [
        "I have a question about my recent order. Can you provide more information?",
        "I'm interested in a product but need more details before purchasing.",
        "What is your return policy for electronics?",
        "My order seems to be delayed. Can you check the status?"
    ]
    
    for user in registered_users:
        # Login to get token
        token = login_user(user)
        if not token:
            continue
            
        # Create ticket with random subject and message
        subject_index = random.randint(0, len(ticket_subjects) - 1)
        
        # Try different ticket data formats
        ticket_formats = [
            {
                "subject": ticket_subjects[subject_index],
                "message": ticket_messages[subject_index],
                "priority": random.choice(["low", "medium", "high"])
            },
            {
                "title": ticket_subjects[subject_index],
                "description": ticket_messages[subject_index],
                "priority": random.choice(["low", "medium", "high"]),
                "user_id": user.get("id", 1)
            },
            {
                "subject": ticket_subjects[subject_index],
                "body": ticket_messages[subject_index],
                "priority": random.choice(["low", "medium", "high"]),
                "customer_id": user.get("id", 1),
                "email": user.get("email", "user@example.com")
            }
        ]
        
        # Try different endpoints
        endpoints = [
            f"{CUSTOMER_SUPPORT_URL}/tickets",
            f"{CUSTOMER_SUPPORT_URL}/ticket",
            f"{CUSTOMER_SUPPORT_URL}/api/tickets",
            f"{CUSTOMER_SUPPORT_URL}/support/tickets"
        ]
        
        success = False
        for endpoint in endpoints:
            for ticket_data in ticket_formats:
                try:
                    response = requests.post(
                        endpoint,
                        json=ticket_data,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if response.status_code == 200 or response.status_code == 201:
                        print_colored(f"  ✅ Created support ticket for {user['first_name']} {user['last_name']} via {endpoint}")
                        success = True
                        break
                except requests.RequestException:
                    continue
            if success:
                break
                
        if not success:
            print_colored(f"  ❌ Failed to create support ticket for {user['first_name']} {user['last_name']}: Could not find working endpoint", Colors.YELLOW)

# Global variables to share data between functions
registered_users = []

def main():
    global registered_users
    print_colored("=== Shop-meetingAPI Data Seeding ===", Colors.GREEN)
    print_colored("This script will populate your databases with sample data.\n")
    
    # Check if services are running
    services = [
        ("Auth Service", AUTH_SERVICE_URL),
        ("Profile Service", PROFILE_SERVICE_URL),
        ("Product Service", PRODUCT_SERVICE_URL),
        ("Cart Service", CART_SERVICE_URL),
        ("Order Service", ORDER_SERVICE_URL),
        ("Customer Support Service", CUSTOMER_SUPPORT_URL)
    ]
    
    all_healthy = True
    for service_name, url in services:
        if not check_service_health(service_name, url):
            all_healthy = False
    
    if not all_healthy:
        print_colored("\n[WARNING] Not all services are healthy. Some seeding operations may fail.", Colors.YELLOW)
        print("Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            print_colored("Seeding canceled.", Colors.YELLOW)
            return
    
# ... (rest of the code remains the same)
    print("\nSelect operations to perform:")
    print("1. Register/Login Users")
    print("2. Create User Profiles")
    print("3. Create Products")
    print("4. Add Items to Carts")
    print("5. Create Orders")
    print("6. Create Support Tickets")
    print("7. Run ALL Operations")
    
    choice = input("Enter your choice (1-7) or press Enter for ALL: ")
    
    if choice == "":
        choice = "7"  # Default to ALL
        
    # Start seeding data
    if choice in ["1", "7"]:
        registered_users = register_users()
    
    # Continue with operations based on user choice
    if choice in ["2", "7"] and registered_users:
        create_profiles(registered_users)
        
    if choice in ["3", "7"]:
        create_products()
        
    if choice in ["4", "7"] and registered_users:
        add_items_to_cart(registered_users)
        
    if choice in ["5", "7"] and registered_users:
        create_orders(registered_users)
        
    if choice in ["6", "7"] and registered_users:
        create_support_tickets(registered_users)
    
    print_colored("\n=== Seeding Complete ===", Colors.GREEN)
    print_colored("Your Shop-meetingAPI now has sample data for testing and development.", Colors.GREEN)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Seed data for Shop-meetingAPI')
    parser.add_argument('--users', action='store_true', help='Register/login users')
    parser.add_argument('--profiles', action='store_true', help='Create user profiles')
    parser.add_argument('--products', action='store_true', help='Create products')
    parser.add_argument('--carts', action='store_true', help='Add items to carts')
    parser.add_argument('--orders', action='store_true', help='Create orders')
    parser.add_argument('--tickets', action='store_true', help='Create support tickets')
    parser.add_argument('--all', action='store_true', help='Run all operations')
    parser.add_argument('--non-interactive', action='store_true', help='Run without any interactive prompts')
    
    args = parser.parse_args()
    
    # If no specific arguments provided, run interactive mode
    if not any([args.users, args.profiles, args.products, args.carts, args.orders, args.tickets, args.all]):
        main()
    else:
        print_colored("=== Shop-meetingAPI Data Seeding ===", Colors.GREEN)
        print_colored("This script will populate your databases with sample data.\n")
        
        # Check if services are running
        services = [
            ("Auth Service", AUTH_SERVICE_URL),
            ("Profile Service", PROFILE_SERVICE_URL),
            ("Product Service", PRODUCT_SERVICE_URL),
            ("Cart Service", CART_SERVICE_URL),
            ("Order Service", ORDER_SERVICE_URL),
            ("Customer Support Service", CUSTOMER_SUPPORT_URL)
        ]
        
        all_healthy = True
        for service_name, url in services:
            if not check_service_health(service_name, url):
                all_healthy = False
        
        if not all_healthy and not args.non_interactive:
            print_colored("\n⚠️ Not all services are healthy. Some seeding operations may fail.", Colors.YELLOW)
            print("Continue anyway? (y/n): ", end="")
            if input().lower() != 'y':
                print_colored("Seeding canceled.", Colors.YELLOW)
                sys.exit(1)
        elif not all_healthy and args.non_interactive:
            print_colored("\n[WARNING] Not all services are healthy. Continuing anyway (non-interactive mode).", Colors.YELLOW)
        
        # Start seeding data based on arguments
        if args.users or args.all:
            registered_users = register_users()
        
        if args.profiles or args.all:
            if not registered_users:
                registered_users = register_users()
            create_profiles(registered_users)
        
        if args.products or args.all:
            create_products()
        
        if args.carts or args.all:
            if not registered_users:
                registered_users = register_users()
            add_items_to_cart(registered_users)
        
        if args.orders or args.all:
            if not registered_users:
                registered_users = register_users()
            create_orders(registered_users)
        
        if args.tickets or args.all:
            if not registered_users:
                registered_users = register_users()
            create_support_tickets(registered_users)
        
        print_colored("\n=== Seeding Complete ===", Colors.GREEN)
        print_colored("Your Shop-meetingAPI now has sample data for testing and development.", Colors.GREEN)
