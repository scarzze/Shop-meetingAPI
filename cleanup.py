#!/usr/bin/env python
"""
Cleanup script for Shop-meetingAPI
Removes unnecessary files and prepares the project for GitHub
"""
import os
import shutil
from rich.console import Console

console = Console()

# Files to keep
KEEP_FILES = [
    # Core project files
    "manage_services.py",
    "test_api.py",
    "verify_api_gateway.py",
    "docker-compose.yml",
    "README.md",
    "NGINX_SETUP.md",
    
    # Nginx configuration
    "nginx/shop_api.conf",
]

# Files to remove (relative to project root)
REMOVE_FILES = [
    "simple_gateway.py",
    "api_gateway.log",
    "check_gateway.py",
    "check_individual_services.py",
    "health_status.json",
    "API_GATEWAY.md",
    "nginx/consolidated_nginx.conf",
    "nginx/windows_nginx.conf",
    "nginx/nginx.conf",
]

def cleanup_project():
    """Remove unnecessary files and prepare for GitHub"""
    console.print("[bold blue]Cleaning up Shop-meetingAPI project...[/bold blue]")
    
    # Get project root
    project_root = os.getcwd()
    
    # Track removed files
    removed_files = []
    
    # Remove specified files
    for file_path in REMOVE_FILES:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                removed_files.append(file_path)
                console.print(f"[green]Removed: {file_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error removing {file_path}: {str(e)}[/red]")
        else:
            console.print(f"[yellow]Not found: {file_path}[/yellow]")
    
    # Summary
    if removed_files:
        console.print("\n[bold green]Successfully removed unnecessary files![/bold green]")
        console.print("The project has been streamlined with a single Nginx configuration.")
    else:
        console.print("\n[yellow]No files were removed.[/yellow]")
    
    console.print("\n[bold blue]Project is ready for GitHub![/bold blue]")
    console.print("Use the following commands to push your changes:")
    console.print("[blue]git add .[/blue]")
    console.print("[blue]git commit -m \"Simplified project with unified Nginx configuration\"[/blue]")
    console.print("[blue]git push origin main[/blue]")

if __name__ == "__main__":
    cleanup_project()
