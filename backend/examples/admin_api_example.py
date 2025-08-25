# backend/examples/admin_api_example.py

"""
Example script showing how to make admin API calls with the new origin validation middleware.
This demonstrates both the required headers and error handling.
"""

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../../.env")

# Configuration
BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')

def make_admin_request(endpoint, method='GET', data=None):
    """Make an admin API request with proper headers"""
    
    url = f"{BASE_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': ADMIN_API_KEY,
        # Note: You might also need Authorization header for JWT token
        # 'Authorization': f'Bearer {your_jwt_token}'
    }
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Request successful")
            try:
                return response.json()
            except:
                return response.text
        else:
            print(f"✗ Request failed: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection failed - is the server running?")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_regular_endpoint():
    """Test a regular (non-admin) endpoint"""
    print("=== Testing Regular Endpoint ===")
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ Regular endpoint works")
            print(f"Response: {response.json()}")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()

def test_admin_endpoints():
    """Test admin endpoints with and without API key"""
    print("=== Testing Admin Endpoints ===")
    
    # Test without API key (should fail)
    print("Testing WITHOUT API key:")
    url = f"{BASE_URL}/admin/users"  # Assuming this exists
    try:
        response = requests.get(url)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly rejected without API key")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test with API key (should work if endpoint exists)
    print("Testing WITH API key:")
    if not ADMIN_API_KEY:
        print("✗ No ADMIN_API_KEY found in environment")
        return
    
    # Try a few common admin endpoints
    admin_endpoints = [
        "/admin/users",
        "/api/admin/logs", 
        "/logs/recent"
    ]
    
    for endpoint in admin_endpoints:
        result = make_admin_request(endpoint)
        if result:
            print(f"Data: {str(result)[:100]}{'...' if len(str(result)) > 100 else ''}")
        print()

if __name__ == "__main__":
    print("CertAlert Admin API Example")
    print("=" * 40)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {'***' + ADMIN_API_KEY[-4:] if ADMIN_API_KEY else 'NOT SET'}")
    print()
    
    if not ADMIN_API_KEY:
        print("❌ ADMIN_API_KEY not found in environment variables!")
        print("Make sure your .env file contains: ADMIN_API_KEY=your-key-here")
        exit(1)
    
    test_regular_endpoint()
    test_admin_endpoints()
    
    print("Note: Some endpoints may not exist yet or may require additional authentication (JWT tokens).")
    print("This example shows how to structure your requests with the new middleware.")
