#!/usr/bin/env python
"""
Verification and Preparation Script for Shop-meetingAPI
This script verifies all services are working correctly and prepares the project for GitHub push
"""
import os
import sys
import json
import requests
import subprocess
import time
from rich.console import Console
from rich.table import Table

console = Console()

# Define service configurations
SERVICES = [
    {"name": "Auth Service", "port": 5002, "health_endpoint": "/health"},
    {"name": "Profile Service", "port": 5003, "health_endpoint": "/health"},
    {"name": "Cart Service", "port": 5001, "health_endpoint": "/health"},
    {"name": "Order Service", "port": 5005, "health_endpoint": "/health"},
    {"name": "Customer Support Service", "port": 5004, "health_endpoint": "/health"},
    {"name": "Product Service", "port": 5006, "health_endpoint": "/health"},
]

def verify_services():
    """Verify all microservices are running and healthy"""
    console.print("\n[bold blue]Verifying All Microservices...[/bold blue]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Service")
    table.add_column("URL")
    table.add_column("Status")
    table.add_column("Result")
    
    all_healthy = True
    
    for service in SERVICES:
        service_url = f"http://localhost:{service['port']}{service['health_endpoint']}"
        
        try:
            response = requests.get(service_url, timeout=3)
            status = response.status_code
            
            if status == 200:
                status_text = "[green]HEALTHY[/green]"
                result = "✅ PASSED"
            else:
                status_text = f"[red]ERROR ({status})[/red]"
                result = "❌ FAILED"
                all_healthy = False
                
        except requests.RequestException as e:
            status = "ERROR"
            status_text = f"[red]NOT RUNNING[/red]"
            result = f"❌ FAILED: {str(e)[:30]}"
            all_healthy = False
        
        table.add_row(
            service["name"],
            service_url,
            status_text,
            result
        )
    
    console.print(table)
    
    if all_healthy:
        console.print("[bold green]All services are healthy! Ready for GitHub push.[/bold green]")
    else:
        console.print("[bold red]Some services are not running or responding correctly.[/bold red]")
        console.print("Run the following command to start all services:")
        console.print("[blue]python manage_services.py debug --local-db[/blue]")
    
    return all_healthy

def verify_files():
    """Verify all necessary files are present and properly configured"""
    console.print("\n[bold blue]Verifying Project Files...[/bold blue]")
    
    # Create results table
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("File")
    table.add_column("Status")
    
    required_files = [
        "docker-compose.yml",
        "manage_services.py",
        "README.md",
        "API_GATEWAY.md",
        "nginx/consolidated_nginx.conf",
        "nginx/windows_nginx.conf",
        "simple_gateway.py",
        "test_api.py"
    ]
    
    all_files_present = True
    
    for file_path in required_files:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            table.add_row(file_path, "[green]PRESENT[/green]")
        else:
            table.add_row(file_path, "[red]MISSING[/red]")
            all_files_present = False
    
    console.print(table)
    
    if all_files_present:
        console.print("[bold green]All required files are present![/bold green]")
    else:
        console.print("[bold red]Some required files are missing.[/bold red]")
    
    return all_files_present

def prepare_for_github():
    """Prepare project for GitHub push"""
    console.print("\n[bold blue]Preparing for GitHub Push...[/bold blue]")
    
    # Create a health status summary file
    health_status = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": {}
    }
    
    for service in SERVICES:
        service_url = f"http://localhost:{service['port']}{service['health_endpoint']}"
        
        try:
            response = requests.get(service_url, timeout=3)
            if response.status_code == 200:
                health_status["services"][service["name"]] = "HEALTHY"
            else:
                health_status["services"][service["name"]] = f"ERROR ({response.status_code})"
        except requests.RequestException:
            health_status["services"][service["name"]] = "NOT RUNNING"
    
    # Write health status to file
    with open("health_status.json", "w") as f:
        json.dump(health_status, f, indent=2)
    
    console.print("Created [blue]health_status.json[/blue] with current service status.")
    console.print("\n[bold green]Project is ready for GitHub push![/bold green]")
    console.print("Use the following commands to push to GitHub:")
    console.print("[blue]git add .[/blue]")
    console.print("[blue]git commit -m \"Fixed all services and added Ubuntu compatibility\"[/blue]")
    console.print("[blue]git push origin main[/blue]")

if __name__ == "__main__":
    console.print("[bold]Shop-meetingAPI Verification and Preparation[/bold]")
    
    services_ok = verify_services()
    files_ok = verify_files()
    
    if services_ok and files_ok:
        prepare_for_github()
        console.print("\n[bold green]SUCCESS! Project is fully prepared and ready for use.[/bold green]")
        sys.exit(0)
    else:
        console.print("\n[bold yellow]WARNING: Please address the issues above before pushing to GitHub.[/bold yellow]")
        sys.exit(1)
