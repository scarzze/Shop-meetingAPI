#!/usr/bin/env python3
import subprocess
import time
import sys
from datetime import datetime
import requests
import signal
from typing import List, Dict

# Order of shutdown (reverse of startup dependencies)
SHUTDOWN_ORDER = [
    'customer-support',
    'order-service',
    'profile-service',
    'cart-service',
    'auth-service',
    'postgres'
]

def get_running_containers() -> Dict[str, str]:
    """Get currently running containers and their IDs"""
    try:
        result = subprocess.run(
            ['docker-compose', 'ps', '-q'],
            capture_output=True,
            text=True,
            check=True
        )
        container_ids = result.stdout.strip().split('\n')
        
        containers = {}
        for container_id in container_ids:
            if not container_id:
                continue
            # Get container name
            result = subprocess.run(
                ['docker', 'inspect', '-f', '{{.Name}}', container_id],
                capture_output=True,
                text=True,
                check=True
            )
            name = result.stdout.strip().lstrip('/')
            containers[name] = container_id
        
        return containers
    except subprocess.CalledProcessError as e:
        print(f"Error getting container status: {e}")
        return {}

def check_service_connections(service: str) -> List[str]:
    """Check active connections to a service"""
    try:
        result = subprocess.run(
            ['docker', 'exec', service, 'netstat', '-tn'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [line for line in result.stdout.split('\n') if 'ESTABLISHED' in line]
        return []
    except:
        return []

def graceful_stop_service(service: str, container_id: str) -> bool:
    """Stop a service gracefully"""
    print(f"\nStopping {service}...")
    
    # Check for active connections
    active_connections = check_service_connections(container_id)
    if active_connections:
        print(f"Service has {len(active_connections)} active connections")
        print("Waiting for connections to close...")
        time.sleep(5)  # Give connections time to close
    
    try:
        # Send SIGTERM first
        subprocess.run(
            ['docker', 'stop', '-t', '10', container_id],
            check=True,
            capture_output=True
        )
        print(f"✅ {service} stopped gracefully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to stop {service} gracefully: {e}")
        try:
            # Force stop if graceful shutdown fails
            subprocess.run(
                ['docker', 'kill', container_id],
                check=True,
                capture_output=True
            )
            print(f"⚠️ {service} force stopped")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to force stop {service}: {e}")
            return False

def main():
    print("Starting graceful shutdown sequence...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get running containers
    containers = get_running_containers()
    if not containers:
        print("No containers running")
        sys.exit(0)
    
    # Stop services in order
    failed_services = []
    for service in SHUTDOWN_ORDER:
        if service in containers:
            if not graceful_stop_service(service, containers[service]):
                failed_services.append(service)
    
    # Final cleanup
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Warning: Error during final cleanup: {e}")
    
    if failed_services:
        print("\n⚠️ Some services failed to stop gracefully:")
        for service in failed_services:
            print(f"❌ {service}")
        sys.exit(1)
    else:
        print("\n✅ All services stopped gracefully")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)