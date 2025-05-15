#!/usr/bin/env python
"""
Nginx Gateway Test Script for Shop-meetingAPI
Tests the Nginx gateway connection to all microservices
"""
import requests
import json
import sys
from rich.console import Console
from rich.table import Table

console = Console()

# Nginx gateway URL
NGINX_URL = "http://localhost:9000"

# Service endpoints to test
SERVICES = [
    {"name": "API Gateway", "endpoint": "/api/v1/health"},
    {"name": "Auth Service", "endpoint": "/api/v1/auth/health"},
    {"name": "Profile Service", "endpoint": "/api/v1/profile/health"},
    {"name": "Cart Service", "endpoint": "/api/v1/cart/health"},
    {"name": "Order Service", "endpoint": "/api/v1/order/health"},
    {"name": "Customer Support", "endpoint": "/api/v1/customer-support/health"},
    {"name": "Product Service", "endpoint": "/api/v1/product/health"}
]

def test_nginx_gateway():
    """Test the Nginx gateway connection to all services"""
    console.print("[bold]Shop-meetingAPI Nginx Gateway Test[/bold]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Service")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("Result")
    
    all_passed = True
    
    # First check if Nginx is running
    try:
        console.print("\nChecking if Nginx gateway is running...")
        response = requests.get(f"{NGINX_URL}", timeout=3)
        if response.status_code == 200:
            console.print("[green]✅ Nginx gateway is running![/green]")
        else:
            console.print(f"[yellow]⚠️ Nginx gateway returned status {response.status_code}[/yellow]")
    except requests.RequestException as e:
        console.print(f"[bold red]❌ Nginx gateway is not running or not accessible: {str(e)}[/bold red]")
        console.print("\nPossible fixes:")
        console.print("1. Make sure Nginx is installed and running")
        console.print("2. Verify the configuration at nginx/shop_api.conf is properly loaded")
        console.print("3. Check that port 9000 is not being used by another application")
        return False
    
    # Test each service endpoint
    for service in SERVICES:
        endpoint_url = f"{NGINX_URL}{service['endpoint']}"
        try:
            console.print(f"Testing {service['name']} via {endpoint_url}...")
            response = requests.get(endpoint_url, timeout=5)
            status = response.status_code
            
            if status == 200:
                status_text = f"[green]{status}[/green]"
                result_text = "[green]✅ PASSED[/green]"
            else:
                status_text = f"[red]{status}[/red]"
                result_text = "[red]❌ FAILED[/red]"
                all_passed = False
        except requests.RequestException as e:
            status_text = "[red]ERROR[/red]"
            result_text = f"[red]❌ {str(e)[:30]}[/red]"
            all_passed = False
            
        table.add_row(
            service["name"],
            service["endpoint"],
            status_text,
            result_text
        )
    
    console.print(table)
    
    if all_passed:
        console.print("\n[bold green]SUCCESS! Nginx gateway is properly connected to all microservices.[/bold green]")
    else:
        console.print("\n[bold red]Some services are not properly connected through the Nginx gateway.[/bold red]")
        console.print("Check the Nginx configuration and make sure all services are running.")
    
    return all_passed

if __name__ == "__main__":
    if test_nginx_gateway():
        sys.exit(0)
    else:
        sys.exit(1)
