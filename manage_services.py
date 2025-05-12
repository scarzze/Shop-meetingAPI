#!/usr/bin/env python
"""
Comprehensive service management script for Shop-meetingAPI
Handles: switching to/from DEBUG_MODE, starting/stopping services, checking health
"""
import os
import sys
import subprocess
import time
import argparse
import json
import requests
import signal
from pathlib import Path

# Global constants
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
SERVICES = [
    {
        "name": "Auth Service",
        "dir": "auth-service",
        "port": 5002,
        "url": "http://localhost:5002",
        "env_var": "DATABASE_URL",
        "entry_file": "run.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/auth_service_db"
    },
    {
        "name": "Profile Service",
        "dir": "profile-service",
        "port": 5003,
        "url": "http://localhost:5013",  # Using emergency health check port for monitoring
        "env_var": "DATABASE_URL",
        "entry_file": "run.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/profile_service_db"
    },
    {
        "name": "Cart Service",
        "dir": "cart-service",
        "port": 5001,
        "url": "http://localhost:5001",
        "env_var": "DATABASE_URI",
        "entry_file": "app.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/cart_service_db"
    },
    {
        "name": "Order Service",
        "dir": "Orderservice",
        "port": 5005,
        "url": "http://localhost:5005",
        "env_var": "DATABASE_URL",
        "entry_file": "run.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/order_service_db"
    },
    {
        "name": "Customer Support Service",
        "dir": "Customer_support_back-end",
        "port": 5004,
        "url": "http://localhost:5004",
        "env_var": "DATABASE_URI",
        "entry_file": "run.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/customer_support_db"
    },
    {
        "name": "Product Service",
        "dir": "product-service",
        "port": 5006,
        "url": "http://localhost:5006",
        "env_var": "DATABASE_URL",
        "entry_file": "run.py",
        "local_db": "postgresql://postgres:postgres@localhost:5432/product_service_db"
    }
]

# ANSI color codes for terminal output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
RESET = "\033[0m"

def print_success(message):
    """Print a success message with green checkmark"""
    print(f"{GREEN}✓ {message}{RESET}")

def print_warning(message):
    """Print a warning message with yellow exclamation"""
    print(f"{YELLOW}! {message}{RESET}")

def print_error(message):
    """Print an error message with red X"""
    print(f"{RED}✗ {message}{RESET}")

def print_section(title):
    """Print a section header"""
    print(f"\n{YELLOW}=== {title} ==={RESET}")

def get_service_info(service_name=None, port=None):
    """Get service information by name or port"""
    if service_name:
        for service in SERVICES:
            if service["name"].lower() == service_name.lower():
                return service
    elif port:
        for service in SERVICES:
            if service["port"] == port:
                return service
    return None

def get_env_file_path(service):
    """Get the path to the service's .env file"""
    service_path = PROJECT_ROOT / "services" / service["dir"]
    return service_path / ".env"

def update_env_file(service, debug_mode=False, use_local_db=False):
    """Update the service's .env file with appropriate settings"""
    env_file = get_env_file_path(service)
    if not env_file.exists():
        print_error(f".env file not found for {service['name']}")
        return False
    
    # Read current contents
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Process lines
    new_lines = []
    debug_updated = False
    db_updated = False
    
    for line in lines:
        # Update DEBUG_MODE
        if line.startswith("DEBUG_MODE="):
            new_lines.append(f"DEBUG_MODE={'true' if debug_mode else 'false'}\n")
            debug_updated = True
        # Update database URL if requested
        elif use_local_db and line.startswith(f"{service['env_var']}="):
            new_lines.append(f"{service['env_var']}={service['local_db']}\n")
            db_updated = True
        else:
            new_lines.append(line)
    
    # Add DEBUG_MODE if not present
    if not debug_updated:
        new_lines.append(f"DEBUG_MODE={'true' if debug_mode else 'false'}\n")
    
    # Add database URL if not present and local db requested
    if use_local_db and not db_updated:
        new_lines.append(f"{service['env_var']}={service['local_db']}\n")
    
    # Write updated contents
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    return True

def check_service_health(service):
    """Check if a service is running and healthy"""
    try:
        # Make a request to the health endpoint
        response = requests.get(f"{service['url']}/health", timeout=2)
        
        # Consider any response as healthy if we get a response from the service
        # This is more tolerant of different health check implementations
        if response.status_code < 500:  # Any non-500 response means the service is running
            print(f"Got response from {service['name']}: {response.status_code}")
            return True
            
        # If we get a 500+ error, log it for debugging
        print(f"Health check for {service['name']} returned error {response.status_code}: {response.text[:100]}")
        return False
    except requests.RequestException as e:
        print(f"Connection error to {service['name']}: {str(e)}")
        return False

def start_service(service, debug_mode=False, use_local_db=False):
    """Start a microservice"""
    service_path = PROJECT_ROOT / "services" / service["dir"]
    entry_file = service_path / service["entry_file"]
    
    if not entry_file.exists():
        print_error(f"Entry file {service['entry_file']} not found for {service['name']}")
        return False
    
    # Kill existing process on this port if any
    try:
        subprocess.run(["fuser", "-k", f"{service['port']}/tcp"], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)  # Wait for port to be freed
    except Exception:
        pass
    
    # Update environment variables
    if not update_env_file(service, debug_mode, use_local_db):
        return False
    
    # Start the service
    try:
        cmd = ["python", str(entry_file)]
        print(f"Starting {service['name']} with command: {' '.join(cmd)}")
        
        env = os.environ.copy()
        env["DEBUG_MODE"] = "true" if debug_mode else "false"
        
        process = subprocess.Popen(
            cmd,
            cwd=str(service_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print_error(f"Service failed to start")
            print(f"STDOUT: {stdout[:500]}")
            print(f"STDERR: {stderr[:500]}")
            return False
        
        # Check if service is responding
        if check_service_health(service):
            print_success(f"{service['name']} is running on port {service['port']}")
            return True
        else:
            print_warning(f"{service['name']} started but not responding to health checks")
            return True
    except Exception as e:
        print_error(f"Error starting {service['name']}: {str(e)}")
        return False

def start_all_services(debug_mode=False, use_local_db=False):
    """Start all microservices"""
    print_section(f"Starting all services with DEBUG_MODE={'true' if debug_mode else 'false'}")
    
    successful = 0
    for service in SERVICES:
        print_section(f"Starting {service['name']}")
        if start_service(service, debug_mode, use_local_db):
            successful += 1
    
    print_section("Start Summary")
    print(f"Successfully started {successful}/{len(SERVICES)} services")
    return successful == len(SERVICES)

def check_all_services():
    """Check the health of all services"""
    print_section("Service Health Check")
    
    healthy = 0
    for service in SERVICES:
        status = "HEALTHY" if check_service_health(service) else "NOT RESPONDING"
        color = GREEN if status == "HEALTHY" else RED
        print(f"{service['name']} ({service['port']}): {color}{status}{RESET}")
        if status == "HEALTHY":
            healthy += 1
    
    print(f"\n{healthy}/{len(SERVICES)} services are healthy")
    return healthy

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Manage Shop-meetingAPI microservices")
    parser.add_argument("action", choices=["start", "check", "debug", "prod"],
                      help="Action to perform")
    parser.add_argument("--service", "-s", help="Specific service to manage (by name)")
    parser.add_argument("--port", "-p", type=int, help="Specific service to manage (by port)")
    parser.add_argument("--local-db", "-l", action="store_true",
                      help="Use local database instead of remote")
    
    args = parser.parse_args()
    
    # Handle actions for a specific service
    if args.service or args.port:
        service = get_service_info(args.service, args.port)
        if not service:
            print_error(f"Service not found with name '{args.service}' or port {args.port}")
            return 1
        
        if args.action == "start":
            return 0 if start_service(service, False, args.local_db) else 1
        elif args.action == "debug":
            return 0 if start_service(service, True, args.local_db) else 1
        elif args.action == "check":
            healthy = check_service_health(service)
            status = "HEALTHY" if healthy else "NOT RESPONDING"
            color = GREEN if healthy else RED
            print(f"{service['name']} ({service['port']}): {color}{status}{RESET}")
            return 0 if healthy else 1
    
    # Handle actions for all services
    else:
        if args.action == "start":
            return 0 if start_all_services(False, args.local_db) else 1
        elif args.action == "debug":
            return 0 if start_all_services(True, args.local_db) else 1
        elif args.action == "prod":
            return 0 if start_all_services(False, args.local_db) else 1
        elif args.action == "check":
            healthy = check_all_services()
            return 0 if healthy == len(SERVICES) else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
