#!/usr/bin/env python
"""
API Testing Script for Shop-meetingAPI
This script tests each service's API endpoints individually to verify their structure.
"""
import os
import sys
import json
import requests

# Base URLs for services
AUTH_SERVICE_URL = "http://localhost:5002"
PROFILE_SERVICE_URL = "http://localhost:5003"
PRODUCT_SERVICE_URL = "http://localhost:5006"
CART_SERVICE_URL = "http://localhost:5001"
ORDER_SERVICE_URL = "http://localhost:5005"
CUSTOMER_SUPPORT_URL = "http://localhost:5004"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_colored(message, color=Colors.GREEN):
    print(f"{color}{message}{Colors.RESET}")

def print_header(title):
    print_colored("\n" + "="*50, Colors.BLUE)
    print_colored(f" {title}", Colors.BLUE)
    print_colored("="*50, Colors.BLUE)

def print_response(resp):
    """Pretty print a response"""
    try:
        print(f"Status Code: {resp.status_code}")
        print("Headers:")
        for key, value in resp.headers.items():
            print(f"  {key}: {value}")
        print("Response Body:")
        try:
            print(json.dumps(resp.json(), indent=2))
        except:
            print(resp.text)
    except Exception as e:
        print(f"Error printing response: {str(e)}")

# Test Auth Service
def test_auth_service():
    print_header("TESTING AUTH SERVICE")
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{AUTH_SERVICE_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test login endpoint
    print_colored("\nTesting Login Endpoint:", Colors.YELLOW)
    try:
        login_data = {
            "email": "john.doe@gmail.com",
            "password": "Password123"
        }
        resp = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_data)
        print_response(resp)
        
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            print_colored(f"\nAccess Token: {token[:20]}...", Colors.GREEN)
            return token
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    return None

# Test Profile Service
def test_profile_service(token):
    print_header("TESTING PROFILE SERVICE")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{PROFILE_SERVICE_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test get profile endpoint
    print_colored("\nTesting Get Profile Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{PROFILE_SERVICE_URL}/", headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test profile update endpoint
    print_colored("\nTesting Update Profile Endpoint:", Colors.YELLOW)
    try:
        profile_data = {
            "phone": "+1234567890",
            "bio": "Updated profile through test script"
        }
        resp = requests.put(f"{PROFILE_SERVICE_URL}/", json=profile_data, headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)

# Test Product Service
def test_product_service(token):
    print_header("TESTING PRODUCT SERVICE")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test get products endpoint
    print_colored("\nTesting Get Products Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{PRODUCT_SERVICE_URL}/api/products")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test create product endpoint
    print_colored("\nTesting Create Product Endpoint:", Colors.YELLOW)
    try:
        product_data = {
            "name": "Test Product",
            "description": "Created from test script",
            "price": 99.99,
            "category_id": 1,
            "sku": "TEST-001",
            "stock_quantity": 10
        }
        resp = requests.post(f"{PRODUCT_SERVICE_URL}/api/products", json=product_data, headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)

# Test Cart Service
def test_cart_service(token):
    print_header("TESTING CART SERVICE")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{CART_SERVICE_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test get cart endpoint
    print_colored("\nTesting Get Cart Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{CART_SERVICE_URL}/cart", headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test add to cart endpoint
    print_colored("\nTesting Add to Cart Endpoint:", Colors.YELLOW)
    try:
        cart_data = {
            "product_id": 1,
            "quantity": 2
        }
        resp = requests.post(f"{CART_SERVICE_URL}/cart/add", json=cart_data, headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)

# Test Order Service
def test_order_service(token):
    print_header("TESTING ORDER SERVICE")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{ORDER_SERVICE_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test create order endpoint
    print_colored("\nTesting Create Order Endpoint:", Colors.YELLOW)
    try:
        order_data = {
            "items": [
                {"product_id": 1, "quantity": 2}
            ],
            "shipping_details": {
                "name": "John Doe",
                "address": "123 Main St, New York, NY 10001, USA",
                "phone": "+1234567890"
            },
            "payment_details": {
                "method": "credit_card",
                "card_number": "************1234",
                "expiry_date": "12/26",
                "card_holder": "John Doe"
            }
        }
        resp = requests.post(f"{ORDER_SERVICE_URL}/orders", json=order_data, headers=headers)
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)

# Test Customer Support Service
def test_customer_support_service(token):
    print_header("TESTING CUSTOMER SUPPORT SERVICE")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test health endpoint
    print_colored("\nTesting Health Endpoint:", Colors.YELLOW)
    try:
        resp = requests.get(f"{CUSTOMER_SUPPORT_URL}/health")
        print_response(resp)
    except Exception as e:
        print_colored(f"Error: {str(e)}", Colors.RED)
    
    # Test endpoints discovery
    print_colored("\nDiscovering available endpoints:", Colors.YELLOW)
    paths_to_try = [
        "/",
        "/tickets",
        "/api/tickets",
        "/ticket",
        "/api/ticket",
        "/support/tickets"
    ]
    
    for path in paths_to_try:
        try:
            resp = requests.get(f"{CUSTOMER_SUPPORT_URL}{path}")
            if resp.status_code != 404:
                print_colored(f"\nFound endpoint: {path}", Colors.GREEN)
                print_response(resp)
        except Exception as e:
            print_colored(f"Error with {path}: {str(e)}", Colors.RED)

def main():
    print_colored("API Testing for Shop-meetingAPI Microservices", Colors.GREEN)
    print("This script will test each service's API structure\n")
    
    token = test_auth_service()
    
    print("\nChoose a service to test (or test all):")
    print("1. Auth Service")
    print("2. Profile Service")
    print("3. Product Service")
    print("4. Cart Service")
    print("5. Order Service")
    print("6. Customer Support Service")
    print("7. Test All Services")
    
    choice = input("Enter your choice (1-7): ")
    
    if choice == "1":
        test_auth_service()
    elif choice == "2":
        test_profile_service(token)
    elif choice == "3":
        test_product_service(token)
    elif choice == "4":
        test_cart_service(token)
    elif choice == "5":
        test_order_service(token)
    elif choice == "6":
        test_customer_support_service(token)
    elif choice == "7":
        token = test_auth_service()
        test_profile_service(token)
        test_product_service(token)
        test_cart_service(token)
        test_order_service(token)
        test_customer_support_service(token)
    else:
        print_colored("Invalid choice. Exiting.", Colors.RED)

if __name__ == "__main__":
    main()
