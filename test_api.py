#!/usr/bin/env python
"""
API Gateway Test Script for Shop-meetingAPI
Verifies that all services are properly accessible through the API gateway
"""
import requests
import time
import sys
from rich.console import Console
from rich.table import Table

console = Console()

# API Gateway base URL (Nginx)
API_GATEWAY = "http://localhost:9000"

# Direct service URLs for testing microservices directly
SERVICES = [
    {"name": "Auth Service", "url": "http://localhost:5002/health", "expected_status": 200},
    {"name": "Profile Service", "url": "http://localhost:5003/health", "expected_status": 200},
    {"name": "Cart Service", "url": "http://localhost:5001/health", "expected_status": 200},
    {"name": "Order Service", "url": "http://localhost:5005/health", "expected_status": 200},
    {"name": "Customer Support", "url": "http://localhost:5004/health", "expected_status": 200},
    {"name": "Product Service", "url": "http://localhost:5006/health", "expected_status": 200},
]

# Gateway-routed endpoints
GATEWAY_ENDPOINTS = [
    {"name": "Gateway Health", "endpoint": "/api/v1/health", "expected_status": 200},
    {"name": "Auth via Gateway", "endpoint": "/api/v1/auth/health", "expected_status": 200},
    {"name": "Profile via Gateway", "endpoint": "/api/v1/profiles/health", "expected_status": 200},
    {"name": "Cart via Gateway", "endpoint": "/api/v1/carts/health", "expected_status": 200},
    {"name": "Order via Gateway", "endpoint": "/api/v1/orders/health", "expected_status": 200},
    {"name": "Customer Support via Gateway", "endpoint": "/api/v1/tickets/health", "expected_status": 200},
    {"name": "Products via Gateway", "endpoint": "/api/v1/products/health", "expected_status": 200},
]

def test_services():
    """Test if all microservices are running and responding to health checks"""
    console.print("[bold blue]Testing Direct Microservice Health...[/bold blue]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Service")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Result")
    
    all_passed = True
    
    # Test each service
    for service in SERVICES:
        try:
            response = requests.get(service['url'], timeout=5)
            status_code = response.status_code
            result = "✅ PASSED" if status_code == service["expected_status"] else f"❌ FAILED (expected {service['expected_status']})"
            if status_code != service["expected_status"]:
                all_passed = False
        except requests.RequestException as e:
            status_code = "ERROR"
            result = f"❌ FAILED: {str(e)}"
            all_passed = False
        
        table.add_row(
            service["name"],
            service["url"],
            str(status_code),
            result
        )
    
    console.print(table)
    
    if all_passed:
        console.print("[bold green]All direct service checks passed! Services are healthy.[/bold green]")
        return True
    else:
        console.print("[bold red]Some services are not responding correctly. See details above.[/bold red]")
        return False

def test_api_gateway():
    """Test if the API gateway is correctly routing requests"""
    console.print("\n[bold blue]Testing API Gateway Routing...[/bold blue]")
    
    # Create results table for API Gateway tests
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Endpoint")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Result")
    
    all_passed = True
    failed_endpoints = []
    
    # First test the base health endpoint to ensure gateway is working
    try:
        base_health_url = f"{API_GATEWAY}/health"
        console.print(f"Testing base gateway health: {base_health_url}")
        response = requests.get(base_health_url, timeout=5)
        console.print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            console.print("[green]Base gateway health check passed![/green]")
        else:
            console.print(f"[red]Base gateway health check failed with status {response.status_code}[/red]")
    except requests.RequestException as e:
        console.print(f"[red]Base gateway health check error: {str(e)}[/red]")
    
    # Now test each specific endpoint
    console.print("Testing individual gateway endpoints...")
    for endpoint in GATEWAY_ENDPOINTS:
        url = f"{API_GATEWAY}{endpoint['endpoint']}"
        try:
            console.print(f"Testing: {url}")
            response = requests.get(url, timeout=5)
            status_code = response.status_code
            console.print(f"Response: {status_code}")
            if response.status_code == endpoint["expected_status"]:
                result = "✅ PASSED"
            else:
                result = f"❌ FAILED (expected {endpoint['expected_status']})"
                all_passed = False
                failed_endpoints.append(endpoint['endpoint'])
                try:
                    response_text = response.text[:100]  # Get first 100 chars of response
                    console.print(f"Response content: {response_text}")
                except:
                    pass
        except requests.RequestException as e:
            status_code = "ERROR"
            result = f"❌ FAILED: {str(e)}"
            all_passed = False
            failed_endpoints.append(endpoint['endpoint'])
        
        table.add_row(
            endpoint["name"],
            url,
            str(status_code),
            result
        )
    
    console.print(table)
    
    if all_passed:
        console.print("[bold green]All API Gateway tests passed! The gateway is correctly routing requests.[/bold green]")
        return True
    else:
        console.print("[bold red]Some API Gateway tests failed. The gateway may not be running or has configuration issues.[/bold red]")
        return False

if __name__ == "__main__":
    console.print("[bold]Shop-meetingAPI Test Suite[/bold]")
    console.print("This will test both direct service health and API gateway routing.")
    
    # Wait for services to be ready
    console.print("Checking if services are ready...")
    all_ready = False
    
    for i in range(3):
        try:
            # Try connecting to the Auth Service as a representative check
            response = requests.get("http://localhost:5002/health", timeout=2)
            if response.status_code == 200:
                all_ready = True
                break
        except requests.RequestException:
            console.print(f"Services not ready, waiting... ({i+1}/3)")
            time.sleep(2)
    
    if not all_ready:
        console.print("[bold red]Services don't appear to be running. Please start them with 'python manage_services.py debug --local-db'[/bold red]")
        sys.exit(1)
    
    # Check if API Gateway is running
    gateway_running = False
    console.print("Checking if API Gateway is running...")
    try:
        response = requests.get(f"{API_GATEWAY}/health", timeout=2)
        gateway_running = True
        console.print("[bold green]API Gateway is running![/bold green]")
    except requests.RequestException:
        console.print("[bold yellow]API Gateway doesn't appear to be running.[/bold yellow]")
        console.print("Please start it with: 'nginx -c /path/to/windows_nginx.conf'")
        console.print("Continuing with direct service tests only...")
    
    # First test direct services
    services_ok = test_services()
    
    # Then test API gateway if it's running
    gateway_ok = False
    if gateway_running:
        gateway_ok = test_api_gateway()
    
    # Final summary
    console.print("\n[bold]Test Summary:[/bold]")
    console.print(f"Direct Services: {'[green]PASSED[/green]' if services_ok else '[red]FAILED[/red]'}")
    console.print(f"API Gateway: {'[green]PASSED[/green]' if gateway_ok else '[red]FAILED[/red]' if gateway_running else '[yellow]NOT TESTED[/yellow]'}")
    
    # Exit with appropriate code
    if gateway_running:
        sys.exit(0 if (services_ok and gateway_ok) else 1)
    else:
        # If gateway wasn't tested, exit based only on services
        sys.exit(0 if services_ok else 1)
