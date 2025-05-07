import os
import shutil
import sys

def main():
    """
    Install the shared authentication utility to each service
    """
    print("Setting up shared authentication utilities for Shop Meeting API services...")
    
    # Get the absolute path to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Services that need the shared authentication
    services = [
        'Auth-service',
        'services/cart-service',
        'services/profile-service',
        'services/Orderservice',
        'services/Customer_support_back-end'
    ]
    
    # Path to the auth_utils.py
    auth_utils_path = os.path.join(project_root, 'shared', 'auth_utils.py')
    
    if not os.path.exists(auth_utils_path):
        print(f"Error: Could not find {auth_utils_path}")
        return 1
    
    # Install to each service
    for service in services:
        service_path = os.path.join(project_root, service)
        
        if not os.path.exists(service_path):
            print(f"Warning: Service path {service_path} does not exist. Skipping.")
            continue
        
        # Determine the target location based on the service structure
        if service == 'Auth-service':
            # Auth service has direct app module
            target_dir = os.path.join(service_path, 'utils')
        elif service == 'services/Customer_support_back-end':
            # Customer support service has app/utils structure
            target_dir = os.path.join(service_path, 'app', 'utils')
        else:
            # Other services typically have utils directly in the service
            target_dir = os.path.join(service_path, 'utils')
        
        # Create the target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy the auth_utils.py file
        target_path = os.path.join(target_dir, 'auth_utils.py')
        shutil.copy2(auth_utils_path, target_path)
        print(f"Installed to {target_path}")
        
        # Create or update an __init__.py file if needed
        init_path = os.path.join(target_dir, '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as init_file:
                init_file.write("# Import shared auth utilities\n")
                init_file.write("from .auth_utils import auth_required, admin_required, support_agent_required\n")
            print(f"Created {init_path}")
    
    print("Setup complete! You can now use the shared authentication utilities in each service.")
    print("To use in production, set DEBUG_MODE=false in your environment variables.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
