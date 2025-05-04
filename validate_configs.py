#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import json
from datetime import datetime

REQUIRED_ENV_VARS = {
    'auth-service': [
        'DATABASE_URL',
        'JWT_SECRET_KEY',
        'PORT'
    ],
    'cart-service': [
        'DATABASE_URI',
        'AUTH_SERVICE_URL',
        'PORT'
    ],
    'profile-service': [
        'DATABASE_URL',
        'AUTH_SERVICE_URL',
        'PORT'
    ],
    'order-service': [
        'DATABASE_URL',
        'AUTH_SERVICE_URL',
        'PORT'
    ],
    'customer-support': [
        'DATABASE_URL',
        'AUTH_SERVICE_URL',
        'PORT'
    ]
}

SERVICE_PORTS = {
    'auth-service': '5002',
    'cart-service': '5001',
    'profile-service': '5003',
    'order-service': '5005',
    'customer-support': '5004'
}

def check_env_file(service_name, service_path):
    """Check if .env file exists and has required variables"""
    env_path = os.path.join(service_path, '.env')
    if not os.path.exists(env_path):
        return False, f"Missing .env file in {service_name}"
    
    load_dotenv(env_path)
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS[service_name]:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        return False, f"Missing required environment variables in {service_name}: {', '.join(missing_vars)}"
    
    # Check port configuration
    port = os.getenv('PORT')
    expected_port = SERVICE_PORTS[service_name]
    if port != expected_port:
        return False, f"Incorrect port in {service_name}. Expected {expected_port}, got {port}"
    
    return True, "Configuration is valid"

def check_service_urls(service_name, service_path):
    """Check if service URLs are configured correctly"""
    env_path = os.path.join(service_path, '.env')
    if not os.path.exists(env_path):
        return True, "No .env file to check URLs"
    
    load_dotenv(env_path)
    auth_url = os.getenv('AUTH_SERVICE_URL')
    
    if auth_url and not auth_url.endswith(':5002'):
        return False, f"Incorrect AUTH_SERVICE_URL in {service_name}. Should end with :5002"
    
    return True, "Service URLs are valid"

def validate_service(service_name, service_path):
    """Validate configuration for a single service"""
    print(f"\nChecking {service_name}...")
    
    # Check .env file and variables
    env_valid, env_message = check_env_file(service_name, service_path)
    if not env_valid:
        print(f"❌ {env_message}")
        return False
    
    # Check service URLs
    urls_valid, urls_message = check_service_urls(service_name, service_path)
    if not urls_valid:
        print(f"❌ {urls_message}")
        return False
    
    print(f"✅ Configuration is valid for {service_name}")
    return True

def main():
    print("Starting configuration validation...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    services = {
        'auth-service': './services/auth-service',
        'cart-service': './services/cart-service',
        'profile-service': './services/profile-service',
        'order-service': './services/Orderservice',
        'customer-support': './services/Customer_support_back-end'
    }
    
    results = {}
    valid_configs = True
    
    for service_name, service_path in services.items():
        results[service_name] = validate_service(service_name, service_path)
        if not results[service_name]:
            valid_configs = False
    
    print("\nValidation Summary:")
    print("="*50)
    for service_name, is_valid in results.items():
        status = "✅" if is_valid else "❌"
        print(f"{status} {service_name}")
    
    # Save results to file
    with open('config_validation.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'all_valid': valid_configs
        }, f, indent=2)
    
    if not valid_configs:
        print("\n⚠️  Some configurations need attention!")
        sys.exit(1)
    else:
        print("\n✅ All configurations are valid!")
        sys.exit(0)

if __name__ == '__main__':
    main()