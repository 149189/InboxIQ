#!/usr/bin/env python3
"""
Authenticated test script to verify the transaction fix
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login_and_test():
    """Login first, then test the endpoints"""
    
    session = requests.Session()
    
    print("🔐 Step 1: Logging in...")
    
    # Try to login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        login_response = session.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
        elif login_response.status_code == 400:
            print("⚠️  Login failed - trying to register first...")
            
            # Try to register
            register_response = session.post(
                f"{BASE_URL}/auth/register/",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Register Status: {register_response.status_code}")
            
            if register_response.status_code in [200, 201]:
                print("✅ Registration successful, now logging in...")
                
                # Try login again
                login_response = session.post(
                    f"{BASE_URL}/auth/login/",
                    json=login_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if login_response.status_code == 200:
                    print("✅ Login after registration successful")
                else:
                    print(f"❌ Login after registration failed: {login_response.status_code}")
                    return False
            else:
                print(f"❌ Registration failed: {register_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Now test the confirm_email endpoint
    print("\n🔄 Step 2: Testing confirm_email endpoint...")
    
    # Test 1: Invalid draft ID (should return 404, not 500)
    test_data = {
        "draft_id": 99999,
        "action": "edit"
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/email/confirm/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Test 1 - Invalid Draft ID:")
        print(f"  Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"  Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"  Response (text): {response.text}")
        
        test1_passed = response.status_code == 404
        if test1_passed:
            print("  ✅ SUCCESS: Got expected 404 for invalid draft_id")
        else:
            print(f"  ❌ FAILED: Expected 404, got {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        test1_passed = False
    
    # Test 2: Invalid action (should return 400, not 500)
    print(f"\n🔄 Step 3: Testing invalid action...")
    
    test_data = {
        "draft_id": 1,
        "action": "invalid_action"
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/email/confirm/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Test 2 - Invalid Action:")
        print(f"  Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"  Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"  Response (text): {response.text}")
        
        test2_passed = response.status_code == 400
        if test2_passed:
            print("  ✅ SUCCESS: Got expected 400 for invalid action")
        else:
            print(f"  ❌ FAILED: Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        test2_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED! Transaction error is fixed.")
        print("✅ The confirm_email endpoint is working correctly.")
    else:
        print("❌ Some tests failed:")
        if not test1_passed:
            print("  - Invalid draft ID test failed")
        if not test2_passed:
            print("  - Invalid action test failed")
    
    return test1_passed and test2_passed

def main():
    print("🚀 Authenticated Test - Transaction Fix Verification")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    
    try:
        success = login_and_test()
        return success
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
