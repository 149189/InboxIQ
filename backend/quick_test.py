#!/usr/bin/env python3
"""
Quick test script to verify the transaction fix
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_confirm_email_endpoint():
    """Test the confirm_email endpoint that was causing the transaction error"""
    
    print("🔄 Testing confirm_email endpoint...")
    
    # Test with invalid draft ID (should return 404, not 500)
    test_data = {
        "draft_id": 99999,
        "action": "edit"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/email/confirm/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 404:
            print("✅ SUCCESS: Got expected 404 for invalid draft_id")
            return True
        elif response.status_code == 500:
            print("❌ FAILED: Still getting 500 error")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the Django server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_action():
    """Test invalid action (should return 400, not 500)"""
    
    print("\n🔄 Testing invalid action...")
    
    test_data = {
        "draft_id": 1,
        "action": "invalid_action"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/email/confirm/",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("✅ SUCCESS: Got expected 400 for invalid action")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Quick Test - Transaction Fix Verification")
    print("=" * 50)
    
    # Test the endpoints
    test1_passed = test_confirm_email_endpoint()
    test2_passed = test_invalid_action()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("✅ All tests passed! Transaction error is fixed.")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
