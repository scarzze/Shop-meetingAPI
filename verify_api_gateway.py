#!/usr/bin/env python
"""
API Gateway Connection Verification
Tests if the API gateway can communicate with all services
"""
import requests
import json
from rich.console import Console
from rich.table import Table

console = Console()

# API Gateway URL (Nginx on port 9000)
API_GATEWAY = "http://localhost:9000"

# Services to check via the API Gateway
SERVICES = [
    {"name": "Auth Service", "endpoint": "/api/v1/auth/health"},
    {"name": "Profile Service", "endpoint": "/api/v1/profile/health"},
    {"name": "Cart Service", "endpoint": "/api/v1/cart/health"},
    {"name": "Order Service", "endpoint": "/api/v1/order/health"},
    {"name": "Customer Support Service", "endpoint": "/api/v1/customer-support/health"},
    {"name": "Product Service", "endpoint": "/api/v1/product/health"},
]

def test_api_gateway_health():
    """Test the API Gateway's overall health endpoint"""
    console.print("\n[bold blue]Testing API Gateway Health Check...[/bold blue]")
    
    try:
        health_url = f"{API_GATEWAY}/api/v1/health"
        console.print(f"Requesting: {health_url}")
        
        response = requests.get(health_url, timeout=5)
        console.print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            console.print(f"Response: {json.dumps(health_data, indent=2)}")
            
            if health_data.get("status") == "UP":
                console.print("[bold green]✅ API Gateway health check PASSED![/bold green]")
                return True
            else:
                console.print("[bold red]❌ API Gateway reports degraded state![/bold red]")
                return False
        else:
            console.print(f"[bold red]❌ API Gateway health check failed with status {response.status_code}[/bold red]")
            return False
            
    except requests.RequestException as e:
        console.print(f"[bold red]❌ Error connecting to API Gateway: {str(e)}[/bold red]")
        return False

def test_service_routing():
    """Test if the API Gateway can route requests to each service"""
    console.print("\n[bold blue]Testing API Gateway Routing to Services...[/bold blue]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Service")
    table.add_column("Gateway Endpoint")
    table.add_column("Status")
    table.add_column("Result")
    
    all_routes_working = True
    
    for service in SERVICES:
        service_url = f"{API_GATEWAY}{service['endpoint']}"
        
        try:
            console.print(f"Testing routing to {service['name']} via {service_url}")
            response = requests.get(service_url, timeout=5)
            status = response.status_code
            
            if status == 200:
                result_text = "[green]✅ PASSED[/green]"
                status_text = f"[green]{status}[/green]"
            else:
                result_text = "[red]❌ FAILED[/red]"
                status_text = f"[red]{status}[/red]"
                all_routes_working = False
                
        except requests.RequestException as e:
            status_text = "[red]ERROR[/red]"
            result_text = f"[red]❌ FAILED: {str(e)[:30]}[/red]"
            all_routes_working = False
        
        table.add_row(
            service["name"],
            service_url,
            status_text,
            result_text
        )
    
    console.print(table)
    
    if all_routes_working:
        console.print("[bold green]All service routing through API Gateway is working![/bold green]")
    else:
        console.print("[bold red]Some services are not properly routed through the API Gateway.[/bold red]")
    
    return all_routes_working

if __name__ == "__main__":
    console.print("[bold]API Gateway Connection Verification[/bold]")
    
    gateway_health = test_api_gateway_health()
    routing_working = test_service_routing()
    
    if gateway_health and routing_working:
        console.print("\n[bold green]SUCCESS! API Gateway is healthy and connected to all services.[/bold green]")
    else:
        console.print("\n[bold red]ISSUES DETECTED: API Gateway is not properly connected to all services.[/bold red]")
        console.print("Check the server logs and verify that the API Gateway is properly configured.")
