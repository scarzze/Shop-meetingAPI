#!/usr/bin/env python
"""
Nginx Cleanup Script
Removes unnecessary Nginx configuration files and backups
"""
import os
import shutil
from rich.console import Console

console = Console()

# Files/directories to remove from nginx directory
REMOVE_ITEMS = [
    "backup",
    "fixed_nginx.conf",
    "simple_nginx.conf"
]

def cleanup_nginx():
    """Remove unnecessary Nginx configuration files"""
    console.print("[bold blue]Cleaning up Nginx configuration files...[/bold blue]")
    
    nginx_dir = os.path.join(os.getcwd(), "nginx")
    if not os.path.exists(nginx_dir):
        console.print("[red]Nginx directory not found![/red]")
        return
    
    for item in REMOVE_ITEMS:
        item_path = os.path.join(nginx_dir, item)
        if os.path.exists(item_path):
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    console.print(f"[green]Removed directory: nginx/{item}[/green]")
                else:
                    os.remove(item_path)
                    console.print(f"[green]Removed file: nginx/{item}[/green]")
            except Exception as e:
                console.print(f"[red]Error removing {item}: {str(e)}[/red]")
        else:
            console.print(f"[yellow]{item} not found in nginx directory[/yellow]")
    
    # Check what's left
    remaining = os.listdir(nginx_dir)
    console.print("\n[bold]Remaining files in nginx directory:[/bold]")
    for file in remaining:
        console.print(f"- {file}")
    
    console.print("\n[bold green]Nginx directory cleaned up successfully![/bold green]")
    console.print("Only the necessary shop_api.conf file is kept for both Windows and Ubuntu compatibility.")

if __name__ == "__main__":
    cleanup_nginx()
