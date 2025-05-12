#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

SERVICES = {
    'auth': './services/auth-service',
    'cart': './services/cart-service',
    'profile': './services/profile-service',
    'order': './services/Orderservice',
    'customer_support': './services/Customer_support_back-end'
}

def check_migrations(service_name, service_path):
    print(f"\nChecking migrations for {service_name}...")
    
    try:
        # Change to service directory
        os.chdir(service_path)
        
        # Run flask db current to check migration status
        result = subprocess.run(
            ['flask', 'db', 'current'],
            capture_output=True,
            text=True,
            env={**os.environ, 'FLASK_APP': 'run.py'}
        )
        
        if result.returncode != 0:
            print(f"❌ Error checking migrations for {service_name}:")
            print(result.stderr)
            return False
            
        if "No migrations found" in result.stdout:
            print(f"⚠️  No migrations found for {service_name}")
            return False
            
        print(f"✅ Migrations are up to date for {service_name}")
        print(f"Current revision: {result.stdout.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking {service_name}: {str(e)}")
        return False
    finally:
        # Return to original directory
        os.chdir('../..')

def main():
    print("Starting migration check...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    original_dir = os.getcwd()
    
    for service_name, service_path in SERVICES.items():
        results[service_name] = check_migrations(service_name, service_path)
        os.chdir(original_dir)  # Ensure we're back in the root directory
    
    print("\nMigration Check Summary:")
    print("="*50)
    all_good = True
    for service_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service_name}")
        if not status:
            all_good = False
    
    if not all_good:
        print("\n⚠️  Some migrations need attention!")
        sys.exit(1)
    else:
        print("\n✅ All migrations are up to date!")
        sys.exit(0)

if __name__ == '__main__':
    main()