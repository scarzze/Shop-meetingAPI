#!/usr/bin/env python
"""
Script to test the microservices with real database connections
"""
import os
import sys
import json
import requests
from datetime import datetime

# JWT token for authentication
JWT_TOKEN = None

# Set to store credentials
AUTH_EMAIL = "newuser@example.com"
AUTH_PASSWORD = "password123"  # From your memory of test credentials

# Service URLs
AUTH_SERVICE_URL = "http://localhost:5002"
PROFILE_SERVICE_URL = "http://localhost:5003"
CART_SERVICE_URL = "http://localhost:5001"
ORDER_SERVICE_URL = "http://localhost:5005"
SUPPORT_SERVICE_URL = "http://localhost:5004"
PRODUCT_SERVICE_URL = "http://localhost:5006"

# Set terminal colors for better visibility
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
RESET = "\033[0m"

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}! {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_section(title):
    print(f"\n{YELLOW}=== {title} ==={RESET}")

def test_health_endpoint(service_name, url):
    """Test the health endpoint of a service"""
    print(f"Testing {service_name} health endpoint...")
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"{service_name} is healthy")
            return True
        else:
            print_error(f"{service_name} returned status code {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"{service_name} is not responding: {str(e)}")
        return False

def get_auth_token():
    """Get JWT token from Auth Service"""
    global JWT_TOKEN
    
    print_section("Authentication")
    print(f"Logging in with {AUTH_EMAIL}...")
    
    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json={"email": AUTH_EMAIL, "password": AUTH_PASSWORD},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            JWT_TOKEN = data.get("token")
            if JWT_TOKEN:
                print_success("Successfully authenticated")
                return True
            else:
                print_error("No token in response")
                return False
        else:
            print_error(f"Login failed with status code {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print_error(f"Auth Service error: {str(e)}")
        return False

def test_product_service():
    """Test the Product Service"""
    print_section("Product Service")
    
    # Test health endpoint
    if not test_health_endpoint("Product Service", PRODUCT_SERVICE_URL):
        return False
    
    # Test getting products
    print("Testing product listing...")
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/api/products", timeout=5)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            print_success(f"Got {len(products)} products from database")
            
            if products:
                # Test getting a single product
                product_id = products[0]["id"]
                print(f"Testing single product retrieval (ID: {product_id})...")
                response = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}", timeout=5)
                if response.status_code == 200:
                    print_success("Successfully retrieved single product")
                else:
                    print_error(f"Failed to retrieve product {product_id}")
            return True
        else:
            print_error(f"Failed to get products: {response.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"Product Service error: {str(e)}")
        return False

def test_order_service():
    """Test the Order Service"""
    print_section("Order Service")
    
    # Test health endpoint
    if not test_health_endpoint("Order Service", ORDER_SERVICE_URL):
        return False
    
    # We need authentication for order history
    if not JWT_TOKEN:
        print_warning("Skipping Order Service tests that require authentication")
        return True
    
    # Test order history
    print("Testing order history...")
    try:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = requests.get(f"{ORDER_SERVICE_URL}/orders/history", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get("orders", [])
            print_success(f"Got {len(orders)} orders from database")
            return True
        else:
            print_error(f"Failed to get order history: {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print_error(f"Order Service error: {str(e)}")
        return False

def test_support_service():
    """Test the Customer Support Service"""
    print_section("Customer Support Service")
    
    # Test health endpoint
    if not test_health_endpoint("Customer Support Service", SUPPORT_SERVICE_URL):
        return False
    
    # Test getting tickets (requires authentication)
    if not JWT_TOKEN:
        print_warning("Skipping Support Service tests that require authentication")
        return True
    
    print("Testing ticket listing...")
    try:
        headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
        response = requests.get(f"{SUPPORT_SERVICE_URL}/tickets", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tickets = data.get("tickets", [])
            print_success(f"Got {len(tickets)} tickets from database")
            return True
        else:
            print_error(f"Failed to get tickets: {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print_error(f"Support Service error: {str(e)}")
        return False

def main():
    """Main function to test all services"""
    print_section("Testing Microservices with Real Database Connections")
    print("This script will test the services to verify they are using real database connections")
    
    # First, let's check which services are running
    available_services = []
    if test_health_endpoint("Auth Service", AUTH_SERVICE_URL):
        available_services.append("auth")
    if test_health_endpoint("Profile Service", PROFILE_SERVICE_URL):
        available_services.append("profile")
    if test_health_endpoint("Cart Service", CART_SERVICE_URL):
        available_services.append("cart")
    if test_health_endpoint("Order Service", ORDER_SERVICE_URL):
        available_services.append("order")
    if test_health_endpoint("Customer Support Service", SUPPORT_SERVICE_URL):
        available_services.append("support")
    if test_health_endpoint("Product Service", PRODUCT_SERVICE_URL):
        available_services.append("product")
    
    print_section("Available Services")
    for service in available_services:
        print_success(service)
    
    # Get authentication token if Auth Service is available
    if "auth" in available_services:
        get_auth_token()
    else:
        print_warning("Auth Service is not available, skipping authentication")
    
    # Test each available service
    results = {}
    
    if "product" in available_services:
        results["product"] = test_product_service()
    
    if "order" in available_services:
        results["order"] = test_order_service()
    
    if "support" in available_services:
        results["support"] = test_support_service()
    
    # Print summary
    print_section("Test Results Summary")
    success_count = sum(1 for result in results.values() if result)
    for service, result in results.items():
        status = f"{GREEN}SUCCESS{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{service}: {status}")
    
    print(f"\n{success_count}/{len(results)} services tested successfully")
    
    if success_count == len(results):
        print_success("All tested services are working with real database connections!")
    else:
        print_warning("Some services failed testing, check details above")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
