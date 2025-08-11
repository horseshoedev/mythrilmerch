#!/usr/bin/env python3
"""
Test script to verify rate limiting functionality
"""

import requests
import time
import json

# Configuration
BASE_URL = "http://localhost:5000"
TEST_ENDPOINT = "/products"

def test_rate_limiting():
    """Test rate limiting by making multiple rapid requests"""
    print("🧪 Testing Rate Limiting")
    print("=" * 40)
    
    # Test 1: Make requests within rate limit
    print("\n📊 Test 1: Making 30 requests (should all succeed)")
    successful_requests = 0
    failed_requests = 0
    
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}{TEST_ENDPOINT}")
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Request {i+1}: Success (200)")
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
            response = requests.get(f"{BASE_URL}{TEST_ENDPOINT}")
            if response.status_code == 200:
                successful_requests += 1
                print(f"✅ Request {i+1}: Success (200)")
            elif response.status_code == 429:
                rate_limited_requests += 1
                print(f"🚫 Request {i+1}: Rate Limited (429)")
                # Try to get retry-after header
                retry_after = response.headers.get('Retry-After', 'unknown')
                print(f"   Retry-After: {retry_after} seconds")
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
            else:
                print(f"❌ Health check {i+1}: Failed ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health check {i+1}: Error - {e}")
        
        time.sleep(0.1)
    
    print(f"\n📈 Health check results: {health_successful}/10 successful")
    
    # Test 4: Wait and retry after rate limit
    print("\n⏰ Test 4: Waiting 60 seconds and retrying...")
    print("Waiting for rate limit to reset...")
    time.sleep(60)
    
    print("Retrying after rate limit reset...")
    try:
        response = requests.get(f"{BASE_URL}{TEST_ENDPOINT}")
        if response.status_code == 200:
            print("✅ Rate limit reset successful - request went through")
        else:
            print(f"❌ Rate limit reset failed - got status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Rate limit reset failed - error: {e}")

def test_different_endpoints():
    """Test rate limiting on different endpoints"""
    print("\n🔍 Testing Different Endpoints")
    print("=" * 40)
    
    endpoints = [
        "/products",
        "/cart",
        "/cart/add",
        "/health"
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Testing endpoint: {endpoint}")
        try:
            if endpoint == "/cart/add":
                # POST request for cart/add
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json={"productId": 1, "quantity": 1})
            else:
                # GET request for other endpoints
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 429:
                print(f"   Rate Limited: Yes")
            else:
                print(f"   Rate Limited: No")
                
        except requests.exceptions.RequestException as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    print("🚀 MythrilMerch Rate Limiting Test")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the Flask server first.")
        print("   Run: python app.py")
        exit(1)
    
    # Run tests
    test_rate_limiting()
    test_different_endpoints()
    
    print("\n🎉 Rate limiting tests completed!")
    print("\n💡 Tips:")
    print("- Rate limits are per IP address")
    print("- Health endpoint is not rate limited")
    print("- Rate limits reset after the time period")
    print("- Check logs for rate limit violations") 