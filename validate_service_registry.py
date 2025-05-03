#!/usr/bin/env python3
import os
import sys
import json
import yaml
from typing import Dict, List, Set
from datetime import datetime

def load_docker_compose() -> dict:
    """Load the docker-compose.yml configuration"""
    try:
        with open('docker-compose.yml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading docker-compose.yml: {e}")
        sys.exit(1)

def load_health_checker() -> dict:
    """Load the health checker configuration"""
    try:
        with open('health_checker.py', 'r') as f:
            content = f.read()
            # Extract SERVICES dictionary using simple parsing
            start = content.find('SERVICES = {')
            end = content.find('}', start)
            while content.find('}', end + 1) > 0 and content[end:].find('{') > 0:
                end = content.find('}', end + 1)
            services_str = content[start:end + 1]
            # Convert string to dictionary safely
            local_dict = {}
            exec(services_str, {}, local_dict)
            return local_dict.get('SERVICES', {})
    except Exception as e:
        print(f"Error loading health_checker.py: {e}")
        sys.exit(1)

def load_diagnostics() -> dict:
    """Load the diagnostics configuration"""
    try:
        with open('diagnose_services.py', 'r') as f:
            content = f.read()
            # Extract SERVICE_TESTS dictionary
            start = content.find('SERVICE_TESTS = {')
            end = content.find('}', start)
            while content.find('}', end + 1) > 0 and content[end:].find('{') > 0:
                end = content.find('}', end + 1)
            services_str = content[start:end + 1]
            # Convert string to dictionary safely
            local_dict = {}
            exec(services_str, {}, local_dict)
            return local_dict.get('SERVICE_TESTS', {})
    except Exception as e:
        print(f"Error loading diagnose_services.py: {e}")
        sys.exit(1)

def validate_services() -> List[str]:
    """Validate service configurations across all files"""
    issues = []
    
    # Load configurations
    compose_config = load_docker_compose()
    health_config = load_health_checker()
    diagnostics_config = load_diagnostics()
    
    # Get service sets
    compose_services = set(
        service for service in compose_config.get('services', {}).keys()
        if service not in ['postgres', 'health-checker']
    )
    health_services = set(health_config.keys())
    diagnostics_services = set(diagnostics_config.keys())
    
    # Check for missing services
    all_services = compose_services | health_services | diagnostics_services
    
    for service in all_services:
        if service not in compose_services:
            issues.append(f"Service '{service}' missing from docker-compose.yml")
        if service not in health_services:
            issues.append(f"Service '{service}' missing from health_checker.py")
        if service not in diagnostics_services:
            issues.append(f"Service '{service}' missing from diagnose_services.py")
    
    # Validate ports
    expected_ports = {
        'auth-service': 5002,
        'cart-service': 5001,
        'profile-service': 5003,
        'order-service': 5005,
        'customer-support': 5004
    }
    
    for service, expected_port in expected_ports.items():
        if service in compose_services:
            service_config = compose_config['services'][service]
            ports = service_config.get('ports', [])
            port_found = False
            for port in ports:
                if isinstance(port, str):
                    host_port = int(port.split(':')[0])
                else:
                    host_port = port
                if host_port == expected_port:
                    port_found = True
                    break
            if not port_found:
                issues.append(f"Service '{service}' not using expected port {expected_port}")
    
    # Validate health checks
    for service in compose_services:
        service_config = compose_config['services'][service]
        if 'healthcheck' not in service_config:
            issues.append(f"Service '{service}' missing healthcheck configuration")
    
    # Validate environment variables
    required_env_vars = {
        'auth-service': ['DATABASE_URL', 'JWT_SECRET_KEY'],
        'cart-service': ['DATABASE_URL', 'AUTH_SERVICE_URL'],
        'profile-service': ['DATABASE_URL', 'AUTH_SERVICE_URL'],
        'order-service': ['DATABASE_URL', 'AUTH_SERVICE_URL'],
        'customer-support': ['DATABASE_URL', 'AUTH_SERVICE_URL']
    }
    
    for service, required_vars in required_env_vars.items():
        if service in compose_services:
            service_config = compose_config['services'][service]
            env_vars = service_config.get('environment', [])
            env_keys = set()
            for env in env_vars:
                if isinstance(env, str):
                    key = env.split('=')[0]
                else:
                    key = env
                env_keys.add(key)
            
            for var in required_vars:
                if var not in env_keys:
                    issues.append(f"Service '{service}' missing required environment variable '{var}'")
    
    return issues

def main():
    print("Validating service registry...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    issues = validate_services()
    
    if issues:
        print("Found configuration issues:")
        for issue in issues:
            print(f"❌ {issue}")
        
        # Save issues to file
        with open('service_registry_issues.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'issues': issues
            }, f, indent=2)
        
        print("\n⚠️  Service registry validation failed!")
        sys.exit(1)
    else:
        print("✅ All services properly registered and configured!")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)