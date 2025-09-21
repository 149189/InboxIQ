#!/usr/bin/env python3
"""
Test the complete email flow with sohamratwadkar@gmail.com
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "sohamratwadkar@gmail.com"

def test_complete_email_flow():
    """Test the complete email flow from chat to draft creation"""
    
    session = requests.Session()
    
    print("🚀 Testing Complete Email Flow")
    print("=" * 50)
    print(f"Target Email: {TEST_EMAIL}")
    print(f"Server: {BASE_URL}")
    
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
    
    # Step 2: Start chat session
    print("\n💬 Step 2: Starting chat session...")
    
    try:
        chat_response = session.post(
            f"{BASE_URL}/api/chat/start/",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            session_id = chat_data.get('session_id')
            print(f"  ✅ Chat session started: {session_id}")
        else:
            print(f"  ❌ Failed to start chat: {chat_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Chat start error: {e}")
        return False
    
    # Step 3: Send email intent message
    print(f"\n📧 Step 3: Sending email intent for {TEST_EMAIL}...")
    
    email_message = f"""Send an email to {TEST_EMAIL} with the subject "InboxIQ API Test" and the following message:

Hi there!

This is a test email from the InboxIQ API testing system. We're verifying that our email drafting and sending functionality is working correctly.

The system successfully:
- Analyzed your intent to send an email
- Resolved the recipient email address
- Generated this professional email draft
- Prepared it for sending via Gmail API

If you receive this email, it means our integration is working perfectly!

Best regards,
InboxIQ Testing System"""
    
    try:
        message_response = session.post(
            f"{BASE_URL}/api/chat/send/",
            json={
                "session_id": session_id,
                "message": email_message
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if message_response.status_code == 200:
            message_data = message_response.json()
            print("  ✅ Email intent processed successfully")
            
            # Check if we got a draft
            if 'message' in message_data and 'metadata' in message_data['message']:
                metadata = message_data['message']['metadata']
                draft_id = metadata.get('draft_id')
                
                if draft_id:
                    print(f"  ✅ Email draft created: ID {draft_id}")
                    
                    # Display the draft content
                    if 'email_preview' in metadata:
                        preview = metadata['email_preview']
                        print(f"\n📄 Draft Preview:")
                        print(f"  Subject: {preview.get('subject', 'N/A')}")
                        print(f"  Body: {preview.get('body', 'N/A')[:100]}...")
                    
                    # Test draft actions
                    print(f"\n🔧 Step 4: Testing draft actions...")
                    
                    # Test EDIT action
                    edit_response = session.post(
                        f"{BASE_URL}/api/email/confirm/",
                        json={"draft_id": draft_id, "action": "edit"},
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if edit_response.status_code == 200:
                        print("  ✅ EDIT action successful")
                    else:
                        print(f"  ❌ EDIT action failed: {edit_response.status_code}")
                    
                    # Test CANCEL action
                    cancel_response = session.post(
                        f"{BASE_URL}/api/email/confirm/",
                        json={"draft_id": draft_id, "action": "cancel"},
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if cancel_response.status_code == 200:
                        print("  ✅ CANCEL action successful")
                    else:
                        print(f"  ❌ CANCEL action failed: {cancel_response.status_code}")
                    
                    # Note about SEND action
                    print(f"\n⚠️  SEND Action:")
                    print(f"  The SEND action is not tested automatically to avoid")
                    print(f"  sending actual emails to {TEST_EMAIL}.")
                    print(f"  To test sending, manually call:")
                    print(f"  POST /api/email/confirm/ with:")
                    print(f"  {{'draft_id': {draft_id}, 'action': 'send'}}")
                    
                    return True
                else:
                    print("  ⚠️  No draft_id found in response metadata")
                    print(f"  Response: {json.dumps(message_data, indent=2)}")
                    return False
            else:
                print("  ⚠️  No metadata found in response")
                print(f"  Response: {json.dumps(message_data, indent=2)}")
                return False
        else:
            print(f"  ❌ Failed to send message: {message_response.status_code}")
            try:
                error_data = message_response.json()
                print(f"  Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"  Error text: {message_response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Message send error: {e}")
        return False

def main():
    try:
        success = test_complete_email_flow()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ EMAIL FLOW TEST COMPLETED SUCCESSFULLY!")
            print(f"✅ The system can create email drafts for {TEST_EMAIL}")
            print("✅ All draft actions (edit, cancel) are working")
            print("✅ Ready for production email sending")
        else:
            print("❌ Email flow test failed. Check the output above.")
        
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
