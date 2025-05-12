#!/usr/bin/env python3
import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import time

# Test user credentials for diagnostics
TEST_USER = {
    'email': 'test@example.com',
    'password': 'Test123!',
    'first_name': 'Test',
    'last_name': 'User'
}

SERVICE_TESTS = {
    'auth': {
        'name': 'Authentication Service',
        'base_url': 'http://localhost:5002',
        'endpoints': [
            ('GET', '/health'),
            ('POST', '/auth/register'),
            ('POST', '/auth/login'),
        ]
    },
    'cart': {
        'name': 'Cart Service',
        'base_url': 'http://localhost:5001',
        'endpoints': [
            ('GET', '/health'),
            ('GET', '/cart'),
            ('POST', '/cart/add'),
        ]
    },
    'profile': {
        'name': 'Profile Service',
        'base_url': 'http://localhost:5003',
        'endpoints': [
            ('GET', '/health'),
            ('GET', '/profile'),
            ('GET', '/addresses'),
        ]
    },
    'order': {
        'name': 'Order Service',
        'base_url': 'http://localhost:5005',
        'endpoints': [
            ('GET', '/health'),
            ('GET', '/orders/user/1'),
        ]
    },
    'customer-support': {
        'name': 'Customer Support Service',
        'base_url': 'http://localhost:5004',
        'endpoints': [
            ('GET', '/health'),
            ('GET', '/api/v1/tickets'),
        ]
    }
}

def test_endpoint(method: str, url: str, auth_token: str = None, data: dict = None) -> Tuple[bool, dict]:
    """Test an endpoint and return success status and response"""
    headers = {'Content-Type': 'application/json'}
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)
        else:
            return False, {'error': f'Unsupported method: {method}'}
        
        return response.status_code in [200, 201], {
            'status_code': response.status_code,
            'response': response.json() if response.text else None
        }
    except requests.exceptions.ConnectionError:
        return False, {'error': 'Connection failed'}
    except requests.exceptions.Timeout:
        return False, {'error': 'Request timed out'}
    except Exception as e:
        return False, {'error': str(e)}

def run_integration_test() -> Dict:
    """Run a full integration test across all services"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'integration_tests': []
    }
    
    auth_token = None
    
    # Test individual service health
    for service_id, service in SERVICE_TESTS.items():
        print(f"\nTesting {service['name']}...")
        service_results = []
        
        for method, endpoint in service['endpoints']:
            url = f"{service['base_url']}{endpoint}"
            success, response = test_endpoint(method, url, auth_token)
            
            test_result = {
                'endpoint': endpoint,
                'method': method,
                'success': success,
                'response': response
            }
            service_results.append(test_result)
            
            status = "✅" if success else "❌"
            print(f"{status} {method} {endpoint}")
            
            # Special handling for auth endpoints
            if service_id == 'auth' and endpoint == '/auth/register' and success:
                # Try to register test user
                success, response = test_endpoint('POST', url, data=TEST_USER)
                
            elif service_id == 'auth' and endpoint == '/auth/login' and success:
                # Try to login and get token
                success, response = test_endpoint('POST', url, data={
                    'email': TEST_USER['email'],
                    'password': TEST_USER['password']
                })
                if success and 'access_token' in response.get('response', {}):
                    auth_token = response['response']['access_token']
                    print("✅ Successfully obtained auth token")
                
        results['services'][service_id] = {
            'name': service['name'],
            'tests': service_results,
            'all_passed': all(test['success'] for test in service_results)
        }
    
    # Run integration tests
    print("\nRunning integration tests...")
    if auth_token:
        # Test cart -> auth integration
        success, response = test_endpoint('GET', f"{SERVICE_TESTS['cart']['base_url']}/cart", auth_token)
        results['integration_tests'].append({
            'name': 'Cart-Auth Integration',
            'success': success,
            'response': response
        })
        
        # Test profile -> auth integration
        success, response = test_endpoint('GET', f"{SERVICE_TESTS['profile']['base_url']}/profile", auth_token)
        results['integration_tests'].append({
            'name': 'Profile-Auth Integration',
            'success': success,
            'response': response
        })
        
        # Test order -> auth integration
        success, response = test_endpoint('GET', f"{SERVICE_TESTS['order']['base_url']}/orders/user/1", auth_token)
        results['integration_tests'].append({
            'name': 'Order-Auth Integration',
            'success': success,
            'response': response
        })
    
    return results

def print_summary(results: Dict):
    """Print a summary of the diagnostic results"""
    print("\nDiagnostic Summary:")
    print("="*50)
    
    # Service status summary
    print("\nService Status:")
    all_services_passed = True
    for service_id, service_result in results['services'].items():
        status = "✅" if service_result['all_passed'] else "❌"
        print(f"{status} {service_result['name']}")
        if not service_result['all_passed']:
            all_services_passed = False
    
    # Integration test summary
    print("\nIntegration Tests:")
    all_integrations_passed = True
    for test in results['integration_tests']:
        status = "✅" if test['success'] else "❌"
        print(f"{status} {test['name']}")
        if not test['success']:
            all_integrations_passed = False
    
    # Overall status
    print("\nOverall Status:")
    if all_services_passed and all_integrations_passed:
        print("✅ All services and integrations are working properly")
    else:
        print("⚠️  Some services or integrations need attention")

def main():
    print("Starting service diagnostics...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = run_integration_test()
    
    # Save detailed results to file
    with open('service_diagnostics.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate status code
    all_passed = all(
        service['all_passed'] 
        for service in results['services'].values()
    ) and all(
        test['success'] 
        for test in results['integration_tests']
    )
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)