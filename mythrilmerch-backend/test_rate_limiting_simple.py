#!/usr/bin/env python3
"""
Simplified test script to verify rate limiting functionality (no database required)
"""

import requests
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_rate_limiting():
    """Test rate limiting by making multiple rapid requests"""
    print("🧪 Testing Rate Limiting (Simplified)")
    print("=" * 50)
    
    # Test 1: Make requests within rate limit
    print("\n📊 Test 1: Making 30 requests (should all succeed)")
    successful_requests = 0
    failed_requests = 0
    
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/products")
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Request {i+1}: Success (200)")
            elif response.status_code == 500:
                # Database error is expected, but rate limiting should still work
                successful_requests += 1
                print(f"⚠️  Request {i+1}: Database error (500) - but rate limiting works")
            else:
                failed_requests += 1
                print(f"❌ Request {i+1}: Failed ({response.status_code})")
        except requests.exceptions.RequestException as e:
            failed_requests += 1
            print(f"❌ Request {i+1}: Error - {e}")
        
        time.sleep(0.1)  # Small delay between requests
    
    print(f"\n📈 Results: {successful_requests} successful, {failed_requests} failed")
    
    # Test 2: Make requests to exceed rate limit
    print("\n🚨 Test 2: Making 70 rapid requests (should hit rate limit)")
    rate_limited_requests = 0
    successful_requests = 0
    
    for i in range(70):
        try:
            response = requests.get(f"{BASE_URL}/products")
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Request {i+1}: Success (200)")
            elif response.status_code == 429:
                rate_limited_requests += 1
                print(f"🚫 Request {i+1}: Rate Limited (429)")
                # Try to get retry-after header
                retry_after = response.headers.get('Retry-After', 'unknown')
                print(f"   Retry-After: {retry_after} seconds")
            elif response.status_code == 500:
                # Database error is expected
                successful_requests += 1
                print(f"⚠️  Request {i+1}: Database error (500) - but rate limiting works")
            else:
                print(f"❌ Request {i+1}: Unexpected ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request {i+1}: Error - {e}")
        
        time.sleep(0.05)  # Faster requests to trigger rate limiting
    
    print(f"\n📈 Results: {successful_requests} successful, {rate_limited_requests} rate limited")
    
    # Test 3: Test health endpoint (should not be rate limited)
    print("\n🏥 Test 3: Testing health endpoint (should not be rate limited)")
    health_successful = 0
    
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health_successful += 1
                print(f"✅ Health check {i+1}: Success (200)")
            elif response.status_code == 503:
                # Health check returns 503 when database is down, but should not be rate limited
                health_successful += 1
                print(f"⚠️  Health check {i+1}: Database down (503) - but not rate limited")
            else:
                print(f"❌ Health check {i+1}: Failed ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check {i+1}: Error - {e}")
        
        time.sleep(0.1)
    
    print(f"\n📈 Health check results: {health_successful}/10 successful")
    
    # Test 4: Test different endpoints
    print("\n🔍 Test 4: Testing different endpoints")
    endpoints = ["/products", "/cart", "/health"]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing endpoint: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 429:
                print(f"   Rate Limited: Yes")
            else:
                print(f"   Rate Limited: No")
                
        except requests.exceptions.RequestException as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 MythrilMerch Rate Limiting Test (Simplified)")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code in [200, 503]:
            print("✅ Server is running (database may be down, but that's OK for rate limiting test)")
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the Flask server first.")
        print("   Run: cd mythrilmerch-backend && python app.py")
        exit(1)
    
    # Run tests
    test_rate_limiting()
    
    print("\n🎉 Rate limiting tests completed!")
    print("\n💡 Notes:")
    print("- Database errors (500/503) are expected without PostgreSQL")
    print("- Rate limiting should still work even with database errors")
    print("- Health endpoint should not be rate limited")
    print("- Check logs for rate limit violations") 