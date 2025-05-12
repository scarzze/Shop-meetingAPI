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

def run_command(command, service_path, env=None):
    """Run a command in a service directory"""
    try:
        os.chdir(service_path)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env={**os.environ, **(env or {})}
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def migrate_service(service_name, service_path, action):
    """Run migration action on a service"""
    print(f"\n{'-'*50}")
    print(f"Processing {service_name}...")
    
    env = {'FLASK_APP': 'run.py'}
    
    if action == 'init':
        success, output, error = run_command(['flask', 'db', 'init'], service_path, env)
        if not success:
            if 'already exists' in error:
                print(f"✓ Migrations already initialized for {service_name}")
                return True
            print(f"❌ Failed to initialize migrations for {service_name}:")
            print(error)
            return False
        print(f"✓ Initialized migrations for {service_name}")
        
    elif action == 'migrate':
        # Create migration
        success, output, error = run_command(
            ['flask', 'db', 'migrate', '-m', f"Auto-migration {datetime.now().isoformat()}"],
            service_path,
            env
        )
        if not success:
            print(f"❌ Failed to create migration for {service_name}:")
            print(error)
            return False
        print(f"✓ Created migration for {service_name}")
        
        # Apply migration
        success, output, error = run_command(['flask', 'db', 'upgrade'], service_path, env)
        if not success:
            print(f"❌ Failed to apply migration for {service_name}:")
            print(error)
            return False
        print(f"✓ Applied migration for {service_name}")
        
    elif action == 'upgrade':
        success, output, error = run_command(['flask', 'db', 'upgrade'], service_path, env)
        if not success:
            print(f"❌ Failed to upgrade {service_name}:")
            print(error)
            return False
        print(f"✓ Upgraded {service_name}")
        
    elif action == 'downgrade':
        success, output, error = run_command(['flask', 'db', 'downgrade'], service_path, env)
        if not success:
            print(f"❌ Failed to downgrade {service_name}:")
            print(error)
            return False
        print(f"✓ Downgraded {service_name}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_migrations.py <action>")
        print("Actions: init, migrate, upgrade, downgrade")
        sys.exit(1)
        
    action = sys.argv[1]
    if action not in ['init', 'migrate', 'upgrade', 'downgrade']:
        print(f"Invalid action: {action}")
        print("Valid actions are: init, migrate, upgrade, downgrade")
        sys.exit(1)
    
    print(f"Running {action} for all services...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    original_dir = os.getcwd()
    results = {}
    
    for service_name, service_path in SERVICES.items():
        results[service_name] = migrate_service(service_name, service_path, action)
        os.chdir(original_dir)
    
    print("\nMigration Summary:")
    print("="*50)
    all_good = True
    for service_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service_name}")
        if not status:
            all_good = False
    
    if not all_good:
        print("\n⚠️  Some migrations failed!")
        sys.exit(1)
    else:
        print("\n✅ All migrations completed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()