#!/usr/bin/env python3
"""
Manual InboxIQ API Testing Script

This script provides interactive testing for InboxIQ endpoints.
Use this for manual testing and debugging specific scenarios.

Usage:
    python manual_test.py
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "sohamratwadkar@gmail.com"

def make_request(method, endpoint, data=None, headers=None):
    """Make an HTTP request and display the response"""
    url = f"{BASE_URL}{endpoint}"
    
    if headers is None:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    print(f"\n{'='*60}")
    print(f"🔄 {method.upper()} {url}")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    if data:
        print(f"📤 Request Data:")
        print(json.dumps(data, indent=2))
    
    try:
        session = requests.Session()
        
        if method.upper() == 'GET':
            response = session.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = session.post(url, json=data, headers=headers)
        elif method.upper() == 'OPTIONS':
            response = session.options(url, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower() or 'content-type' in key.lower():
                print(f"   {key}: {value}")
        
        try:
            response_data = response.json()
            print(f"📥 Response Body:")
            print(json.dumps(response_data, indent=2))
            return response_data
        except:
            print(f"📥 Response Body (text):")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            return response.text
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed. Is the server running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_authentication():
    """Test authentication endpoints"""
    print(f"\n🔐 TESTING AUTHENTICATION")
    
    # Test registration
    print(f"\n1️⃣ Testing User Registration")
    make_request('POST', '/auth/register/', {
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    # Test login
    print(f"\n2️⃣ Testing User Login")
    make_request('POST', '/auth/login/', {
        'username': 'testuser', 
        'password': 'testpass123'
    })
    
    # Test session sync
    print(f"\n3️⃣ Testing Session Sync")
    make_request('GET', '/auth/sync-session/')

def test_chat_flow():
    """Test complete chat flow"""
    print(f"\n💬 TESTING CHAT FLOW")
    
    # Start chat session
    print(f"\n1️⃣ Starting Chat Session")
    response = make_request('POST', '/api/chat/start/', {})
    
    if response and 'session_id' in response:
        session_id = response['session_id']
        print(f"✅ Got session_id: {session_id}")
        
        # Send general message
        print(f"\n2️⃣ Sending General Message")
        make_request('POST', '/api/chat/send/', {
            'session_id': session_id,
            'message': 'Hello! How can you help me today?'
        })
        
        # Send email intent
        print(f"\n3️⃣ Sending Email Intent")
        email_response = make_request('POST', '/api/chat/send/', {
            'session_id': session_id,
            'message': f'Send an email to {TEST_EMAIL} about our meeting tomorrow. Tell them we need to discuss the project timeline.'
        })
        
        # Extract draft_id if available
        draft_id = None
        if email_response and 'message' in email_response:
            metadata = email_response['message'].get('metadata', {})
            draft_id = metadata.get('draft_id')
            
        if draft_id:
            print(f"✅ Got draft_id: {draft_id}")
            
            # Test email actions
            print(f"\n4️⃣ Testing Email Edit Action")
            make_request('POST', '/api/email/confirm/', {
                'draft_id': draft_id,
                'action': 'edit'
            })
            
            print(f"\n5️⃣ Testing Email Cancel Action")
            make_request('POST', '/api/email/confirm/', {
                'draft_id': draft_id,
                'action': 'cancel'
            })
        
        # Get chat history
        print(f"\n6️⃣ Getting Chat History")
        make_request('GET', f'/api/chat/history/{session_id}/')
        
    else:
        print("❌ Failed to get session_id")

def test_error_scenarios():
    """Test error handling"""
    print(f"\n🚨 TESTING ERROR SCENARIOS")
    
    # Test invalid JSON
    print(f"\n1️⃣ Testing Invalid JSON")
    try:
        response = requests.post(f"{BASE_URL}/api/chat/send/", 
                               data="invalid json",
                               headers={'Content-Type': 'application/json'})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test missing fields
    print(f"\n2️⃣ Testing Missing Required Fields")
    make_request('POST', '/api/chat/send/', {
        'message': 'test message'
        # missing session_id
    })
    
    # Test invalid draft ID
    print(f"\n3️⃣ Testing Invalid Draft ID")
    make_request('POST', '/api/email/confirm/', {
        'draft_id': 99999,
        'action': 'send'
    })
    
    # Test invalid action
    print(f"\n4️⃣ Testing Invalid Action")
    make_request('POST', '/api/email/confirm/', {
        'draft_id': 1,
        'action': 'invalid_action'
    })

def test_cors():
    """Test CORS headers"""
    print(f"\n🌐 TESTING CORS")
    
    endpoints = [
        '/api/chat/start/',
        '/api/chat/send/', 
        '/api/email/confirm/'
    ]
    
    for endpoint in endpoints:
        print(f"\n🔄 Testing CORS for {endpoint}")
        make_request('OPTIONS', endpoint)

def main():
    """Interactive menu for testing"""
    print(f"""
🚀 InboxIQ Manual API Tester
============================
Server: {BASE_URL}
Test Email: {TEST_EMAIL}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Choose a test to run:
1. Authentication Flow
2. Complete Chat Flow  
3. Error Scenarios
4. CORS Headers
5. All Tests
0. Exit
""")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                test_authentication()
            elif choice == '2':
                test_chat_flow()
            elif choice == '3':
                test_error_scenarios()
            elif choice == '4':
                test_cors()
            elif choice == '5':
                print("🔄 Running all tests...")
                test_authentication()
                test_chat_flow()
                test_error_scenarios()
                test_cors()
                print("\n✅ All tests completed!")
            else:
                print("❌ Invalid choice. Please enter 0-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
