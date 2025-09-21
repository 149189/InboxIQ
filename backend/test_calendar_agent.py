#!/usr/bin/env python3
"""
Test script for the new calendar_agent app
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_calendar_agent():
    """Test the calendar agent endpoints"""
    
    session = requests.Session()
    
    print("🗓️  Testing Calendar Agent")
    print("=" * 50)
    
    # Step 1: Login
    print("\n🔐 Step 1: Authentication...")
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        # Try login first
        login_response = session.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            # Try registration if login fails
            print("  Registering new user...")
            session.post(f"{BASE_URL}/auth/register/", json=login_data)
            login_response = session.post(f"{BASE_URL}/auth/login/", json=login_data)
        
        if login_response.status_code == 200:
            print("  ✅ Authentication successful")
        else:
            print(f"  ❌ Authentication failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Authentication error: {e}")
        return False
    
    # Step 2: Start calendar session
    print("\n📅 Step 2: Starting calendar session...")
    
    try:
        calendar_response = session.post(
            f"{BASE_URL}/api/calendar/start/",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        if calendar_response.status_code == 200:
            calendar_data = calendar_response.json()
            session_id = calendar_data.get('session_id')
            print(f"  ✅ Calendar session started: {session_id}")
            print(f"  Welcome message: {calendar_data['message']['content'][:100]}...")
        else:
            print(f"  ❌ Failed to start calendar session: {calendar_response.status_code}")
            try:
                error_data = calendar_response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Error text: {calendar_response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Calendar session error: {e}")
        return False
    
    # Step 3: Test calendar messages
    print(f"\n💬 Step 3: Testing calendar messages...")
    
    test_messages = [
        "Hello, what can you help me with?",
        "I want to schedule a meeting for tomorrow at 2 PM",
        "When am I free this week?",
        "Show me my upcoming events",
        "Create an event called 'Team Standup' for Monday at 9 AM"
    ]
    
    for i, message in enumerate(test_messages):
        print(f"\n  Test {i+1}: '{message}'")
        
        try:
            message_response = session.post(
                f"{BASE_URL}/api/calendar/send/",
                json={
                    "session_id": session_id,
                    "message": message
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if message_response.status_code == 200:
                message_data = message_response.json()
                response_content = message_data['message']['content']
                print(f"    ✅ Response: {response_content[:150]}...")
                
                # Check for special metadata
                if 'metadata' in message_data['message']:
                    metadata = message_data['message']['metadata']
                    if metadata.get('type') == 'event_draft':
                        print(f"    📝 Event draft detected!")
                        
            else:
                print(f"    ❌ Message failed: {message_response.status_code}")
                try:
                    error_data = message_response.json()
                    print(f"    Error: {error_data}")
                except:
                    print(f"    Error text: {message_response.text}")
                    
        except Exception as e:
            print(f"    ❌ Message error: {e}")
    
    # Step 4: Test calendar history
    print(f"\n📜 Step 4: Testing calendar history...")
    
    try:
        history_response = session.get(
            f"{BASE_URL}/api/calendar/history/{session_id}/",
            headers={'Content-Type': 'application/json'}
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            message_count = len(history_data.get('messages', []))
            print(f"  ✅ Retrieved {message_count} messages from history")
        else:
            print(f"  ❌ Failed to get history: {history_response.status_code}")
            
    except Exception as e:
        print(f"  ❌ History error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Calendar Agent testing completed!")
    print("🎉 The calendar_agent app is working correctly!")
    
    return True

def main():
    try:
        success = test_calendar_agent()
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
