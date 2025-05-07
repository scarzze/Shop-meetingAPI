#!/usr/bin/env python3
import subprocess
import time
import sys
import requests
from datetime import datetime
import os
from typing import Dict, List, Tuple

# Service definitions with dependencies
SERVICES: Dict[str, Dict] = {
    'postgres': {
        'name': 'PostgreSQL',
        'port': 5432,
        'health_check': None,  # Custom check in code
        'dependencies': []
    },
    'auth-service': {
        'name': 'Authentication Service',
        'port': 5002,
        'health_check': 'http://localhost:5002/health',
        'dependencies': ['postgres']
    },
    'cart-service': {
        'name': 'Cart Service',
        'port': 5001,
        'health_check': 'http://localhost:5001/health',
        'dependencies': ['postgres', 'auth-service']
    },
    'profile-service': {
        'name': 'Profile Service',
        'port': 5003,
        'health_check': 'http://localhost:5003/health',
        'dependencies': ['postgres', 'auth-service']
    },
    'order-service': {
        'name': 'Order Service',
        'port': 5005,
        'health_check': 'http://localhost:5005/health',
        'dependencies': ['postgres', 'auth-service']
    },
    'customer-support': {
        'name': 'Customer Support Service',
        'port': 5004,
        'health_check': 'http://localhost:5004/health',
        'dependencies': ['postgres', 'auth-service']
    }
}

def check_postgres() -> bool:
    """Check if PostgreSQL is running"""
    try:
        result = subprocess.run(
            ['pg_isready', '-h', 'localhost', '-p', '5432'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def check_service_health(url: str, retries: int = 3, delay: int = 2) -> bool:
    """Check if a service is healthy via its health check endpoint"""
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(delay)
    return False

def check_port_available(port: int) -> bool:
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', port))
        sock.close()
        return True
    except:
        return False

def validate_environment() -> List[str]:
    """Validate environment before starting services"""
    issues = []
    
    # Check if docker is running
    try:
        subprocess.run(['docker', 'info'], capture_output=True, check=True)
    except:
        issues.append("Docker is not running")
    
    # Check if required ports are available
    for service in SERVICES.values():
        if not check_port_available(service['port']):
            issues.append(f"Port {service['port']} is already in use")
    
    return issues

def start_service(service_id: str) -> Tuple[bool, str]:
    """Start a service and verify it's running"""
    service = SERVICES[service_id]
    print(f"\nStarting {service['name']}...")
    
    # Special handling for postgres
    if service_id == 'postgres':
        if check_postgres():
            print(f"✅ {service['name']} is already running")
            return True, ""
        else:
            return False, "PostgreSQL is not running"
    
    # Check dependencies
    for dep in service['dependencies']:
        dep_service = SERVICES[dep]
        if dep == 'postgres':
            if not check_postgres():
                return False, f"Dependency {dep_service['name']} is not running"
        elif not check_service_health(dep_service['health_check']):
            return False, f"Dependency {dep_service['name']} is not running"
    
    # Start service using docker-compose
    try:
        subprocess.run(
            ['docker-compose', 'up', '-d', service_id],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        return False, f"Failed to start service: {e.stderr}"
    
    # Verify service is running
    if service['health_check']:
        if not check_service_health(service['health_check']):
            return False, "Service failed health check"
    
    print(f"✅ {service['name']} started successfully")
    return True, ""

def main():
    print("Starting all services...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Validate environment
    issues = validate_environment()
    if issues:
        print("Environment validation failed:")
        for issue in issues:
            print(f"❌ {issue}")
        sys.exit(1)
    
    # Start services in dependency order
    started_services = set()
    failed_services = {}
    
    def start_with_deps(service_id: str) -> bool:
        if service_id in started_services:
            return True
        if service_id in failed_services:
            return False
            
        # Start dependencies first
        service = SERVICES[service_id]
        for dep in service['dependencies']:
            if not start_with_deps(dep):
                failed_services[service_id] = f"Dependency {SERVICES[dep]['name']} failed to start"
                return False
        
        # Start the service
        success, error = start_service(service_id)
        if success:
            started_services.add(service_id)
            return True
        else:
            failed_services[service_id] = error
            return False
    
    # Try to start all services
    for service_id in SERVICES:
        start_with_deps(service_id)
    
    # Print summary
    print("\nStartup Summary:")
    print("="*50)
    
    all_success = True
    for service_id, service in SERVICES.items():
        if service_id in started_services:
            print(f"✅ {service['name']}")
        else:
            all_success = False
            error = failed_services.get(service_id, "Unknown error")
            print(f"❌ {service['name']}: {error}")
    
    if not all_success:
        print("\n⚠️  Some services failed to start!")
        sys.exit(1)
    else:
        print("\n✅ All services started successfully!")
        print("\nService URLs:")
        print("-"*50)
        for service_id, service in SERVICES.items():
            if service['health_check']:
                print(f"{service['name']}: http://localhost:{service['port']}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStartup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)