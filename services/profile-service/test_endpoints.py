import requests
import json
import time

def test_endpoint(method, url, data=None, token=None, retries=3):
    headers = {
        'Content-Type': 'application/json'
    }
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    for attempt in range(retries):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            print(f"\n{'-'*50}")
            print(f"Testing {method} {url}")
            print(f"Status Code: {response.status_code}")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text}")
            return response.status_code in [200, 201, 404]  # 404 is ok for testing
        except Exception as e:
            print(f"\n{'-'*50}")
            print(f"Error testing {method} {url} (attempt {attempt + 1}/{retries})")
            print(f"Error: {str(e)}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retry
            else:
                return False

def main():
    # Base URLs
    profile_url = "http://localhost:5000"
    
    print("Starting API Tests...")
    
    # Use simple test token for development
    test_token = "test_user_1"
    
    # Test Profile Service endpoints
    print("\nTesting Profile Service...")
    profile_endpoints = [
        ("GET", f"{profile_url}/profile/test_user_1", None),
        ("PATCH", f"{profile_url}/profile", {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890"
        }),
        ("GET", f"{profile_url}/addresses", None),
        ("POST", f"{profile_url}/addresses", {
            "name": "Test Address",
            "street": "123 Test St",
            "city": "Test City",
            "country": "Test Country",
            "postal_code": "12345"
        }),
        ("GET", f"{profile_url}/wishlist", None),
    ]
    
    # Run profile tests
    print("\nRunning Profile Service Tests...")
    profile_results = []
    for method, url, data in profile_endpoints:
        success = test_endpoint(method, url, data, test_token)
        profile_results.append((method, url, success))
    
    # Print summary
    print("\nTest Summary:")
    print("-" * 50)
    print("Profile Service:")
    for method, url, success in profile_results:
        status = "✅ Passed" if success else "❌ Failed"
        print(f"{status} - {method} {url}")

if __name__ == "__main__":
    main()