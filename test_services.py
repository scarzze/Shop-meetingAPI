#!/usr/bin/env python3
"""
Test script for Shop-meetingAPI microservices
This script tests the functionality of all microservices by making API calls to each service
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Service URLs
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001')
PROFILE_SERVICE_URL = os.getenv('PROFILE_SERVICE_URL', 'http://localhost:5002')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5003')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://localhost:5004')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://localhost:5005')
SUPPORT_SERVICE_URL = os.getenv('SUPPORT_SERVICE_URL', 'http://localhost:5006')
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', 'http://localhost:5000')

# Test user credentials
TEST_USER = {
    'username': 'alice',
    'password': 'password123',
    'email': 'alice@example.com'
}

# Colors for terminal output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_header(message):
    """Print a header message"""
    print(f"\n{YELLOW}{'=' * 80}{NC}")
    print(f"{YELLOW}{message.center(80)}{NC}")
    print(f"{YELLOW}{'=' * 80}{NC}\n")

def print_success(message):
    """Print a success message"""
    print(f"{GREEN}✓ {message}{NC}")

def print_error(message):
    """Print an error message"""
    print(f"{RED}✗ {message}{NC}")

def test_auth_service():
    """Test the authentication service"""
    print_header("Testing Auth Service")
    
    # Test registration
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/register", json=TEST_USER)
        if response.status_code == 201 or "already exists" in response.text:
            print_success("User registration works (or user already exists)")
        else:
            print_error(f"User registration failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Auth Service: {e}")
        return None
    
    # Test login
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/login", 
            json={'username': TEST_USER['username'], 'password': TEST_USER['password']}
        )
        if response.status_code == 200:
            print_success("User login works")
            token = response.json().get('access_token')
            return token
        else:
            print_error(f"User login failed: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Auth Service: {e}")
        return None

def test_profile_service(token):
    """Test the profile service"""
    print_header("Testing Profile Service")
    
    if not token:
        print_error("No authentication token available")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test get profile
    try:
        response = requests.get(f"{PROFILE_SERVICE_URL}/profile", headers=headers)
        if response.status_code == 200:
            print_success("Get profile works")
            profile = response.json()
            print(f"User profile: {json.dumps(profile, indent=2)}")
        else:
            print_error(f"Get profile failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Profile Service: {e}")
    
    # Test update profile
    try:
        update_data = {
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'address': '123 Rabbit Hole Lane',
            'city': 'Wonderland',
            'state': 'WL',
            'zip_code': '12345',
            'phone': '555-123-4567'
        }
        response = requests.put(f"{PROFILE_SERVICE_URL}/profile", headers=headers, json=update_data)
        if response.status_code == 200:
            print_success("Update profile works")
        else:
            print_error(f"Update profile failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Profile Service: {e}")

def test_product_service(token):
    """Test the product service"""
    print_header("Testing Product Service")
    
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # Test get all products
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
        if response.status_code == 200:
            print_success("Get all products works")
            products = response.json()
            print(f"Found {len(products)} products")
            
            if products:
                product_id = products[0]['id']
                
                # Test get product by ID
                response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
                if response.status_code == 200:
                    print_success(f"Get product by ID works (Product ID: {product_id})")
                else:
                    print_error(f"Get product by ID failed: {response.text}")
                
                # Test add review (requires authentication)
                if token:
                    review_data = {
                        'rating': 5,
                        'comment': 'Great product!'
                    }
                    response = requests.post(
                        f"{PRODUCT_SERVICE_URL}/products/{product_id}/reviews", 
                        headers=headers, 
                        json=review_data
                    )
                    if response.status_code == 201:
                        print_success("Add review works")
                    else:
                        print_error(f"Add review failed: {response.text}")
        else:
            print_error(f"Get all products failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Product Service: {e}")

def test_cart_service(token):
    """Test the cart service"""
    print_header("Testing Cart Service")
    
    if not token:
        print_error("No authentication token available")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test get cart
    try:
        response = requests.get(f"{CART_SERVICE_URL}/cart", headers=headers)
        if response.status_code == 200:
            print_success("Get cart works")
            cart = response.json()
            print(f"Cart: {json.dumps(cart, indent=2)}")
            
            # Get a product to add to cart
            product_response = requests.get(f"{PRODUCT_SERVICE_URL}/products")
            if product_response.status_code == 200:
                products = product_response.json()
                if products:
                    product_id = products[0]['id']
                    
                    # Test add item to cart
                    cart_item = {
                        'product_id': product_id,
                        'quantity': 2
                    }
                    response = requests.post(f"{CART_SERVICE_URL}/cart/items", headers=headers, json=cart_item)
                    if response.status_code == 200 or response.status_code == 201:
                        print_success(f"Add item to cart works (Product ID: {product_id})")
                    else:
                        print_error(f"Add item to cart failed: {response.text}")
        else:
            print_error(f"Get cart failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Cart Service: {e}")

def test_order_service(token):
    """Test the order service"""
    print_header("Testing Order Service")
    
    if not token:
        print_error("No authentication token available")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test get orders
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/orders", headers=headers)
        if response.status_code == 200:
            print_success("Get orders works")
            orders = response.json()
            print(f"Found {len(orders)} orders")
            
            # Test create order
            order_data = {
                'payment_method_id': 1,  # Assuming payment method ID 1 exists
                'shipping_address': '123 Rabbit Hole Lane, Wonderland, WL 12345'
            }
            response = requests.post(f"{ORDER_SERVICE_URL}/orders", headers=headers, json=order_data)
            if response.status_code == 201:
                print_success("Create order works")
                order = response.json()
                order_id = order.get('id')
                
                # Test get order details
                if order_id:
                    response = requests.get(f"{ORDER_SERVICE_URL}/orders/{order_id}", headers=headers)
                    if response.status_code == 200:
                        print_success(f"Get order details works (Order ID: {order_id})")
                    else:
                        print_error(f"Get order details failed: {response.text}")
            else:
                print_error(f"Create order failed: {response.text}")
        else:
            print_error(f"Get orders failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Order Service: {e}")

def test_support_service(token):
    """Test the customer support service"""
    print_header("Testing Customer Support Service")
    
    if not token:
        print_error("No authentication token available")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test get tickets
    try:
        response = requests.get(f"{SUPPORT_SERVICE_URL}/tickets", headers=headers)
        if response.status_code == 200:
            print_success("Get tickets works")
            tickets = response.json()
            print(f"Found {len(tickets)} tickets")
            
            # Test create ticket
            ticket_data = {
                'subject': 'Test Ticket',
                'message': 'This is a test ticket created by the test script'
            }
            response = requests.post(f"{SUPPORT_SERVICE_URL}/tickets", headers=headers, json=ticket_data)
            if response.status_code == 201:
                print_success("Create ticket works")
                ticket = response.json()
                ticket_id = ticket.get('id')
                
                # Test get ticket details
                if ticket_id:
                    response = requests.get(f"{SUPPORT_SERVICE_URL}/tickets/{ticket_id}", headers=headers)
                    if response.status_code == 200:
                        print_success(f"Get ticket details works (Ticket ID: {ticket_id})")
                    else:
                        print_error(f"Get ticket details failed: {response.text}")
            else:
                print_error(f"Create ticket failed: {response.text}")
        else:
            print_error(f"Get tickets failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to Customer Support Service: {e}")

def test_api_gateway():
    """Test the API gateway"""
    print_header("Testing API Gateway")
    
    try:
        response = requests.get(f"{API_GATEWAY_URL}/")
        if response.status_code == 200:
            print_success("API Gateway is working")
            gateway_info = response.json()
            print(f"API Gateway info: {json.dumps(gateway_info, indent=2)}")
        else:
            print_error(f"API Gateway test failed: {response.text}")
    except requests.exceptions.RequestException as e:
        print_error(f"Could not connect to API Gateway: {e}")

def main():
    """Main function to run all tests"""
    print_header("Shop-meetingAPI Microservices Test")
    
    # Test API Gateway
    test_api_gateway()
    
    # Test Auth Service and get token
    token = test_auth_service()
    
    # Test other services
    test_profile_service(token)
    test_product_service(token)
    test_cart_service(token)
    test_order_service(token)
    test_support_service(token)
    
    print_header("Test Completed")

if __name__ == "__main__":
    main()
