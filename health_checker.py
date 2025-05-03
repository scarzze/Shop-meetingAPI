import requests
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables with fallbacks to localhost
SERVICES = {
    'auth': os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002') + '/health',
    'cart': os.getenv('CART_SERVICE_URL', 'http://localhost:5001') + '/health',
    'profile': os.getenv('PROFILE_SERVICE_URL', 'http://localhost:5003') + '/health',
    'order': os.getenv('ORDER_SERVICE_URL', 'http://localhost:5005') + '/health',
    'customer-support': os.getenv('CUSTOMER_SUPPORT_URL', 'http://localhost:5004') + '/health'
}

def check_service_health(service_name, url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Service returned status code {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)

def check_all_services():
    results = {}
    timestamp = datetime.now().isoformat()
    all_healthy = True
    
    for service_name, url in SERVICES.items():
        healthy, details = check_service_health(service_name, url)
        results[service_name] = {
            'healthy': healthy,
            'details': details,
            'checked_at': timestamp
        }
        if not healthy:
            all_healthy = False
    
    results['overall_status'] = 'healthy' if all_healthy else 'degraded'
    return results

def monitor_services(interval=30):
    """Monitor services continuously with specified interval in seconds"""
    print(f"Starting health monitoring (checking every {interval} seconds)...")
    
    while True:
        results = check_all_services()
        print("\n" + "="*50)
        print(f"Health Check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print("="*50)
        
        for service, status in results.items():
            if service != 'overall_status':
                health_indicator = "✅" if status['healthy'] else "❌"
                print(f"{health_indicator} {service}: {'Healthy' if status['healthy'] else 'Unhealthy'}")
                if not status['healthy']:
                    print(f"  Details: {status['details']}")
        
        # Save results to file
        with open('health_status.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        time.sleep(interval)

if __name__ == '__main__':
    try:
        monitor_services()
    except KeyboardInterrupt:
        print("\nHealth monitoring stopped.")