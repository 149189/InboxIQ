#!/usr/bin/env python3
"""
InboxIQ Backend API Endpoint Testing Script

This script tests all the Gmail agent endpoints with comprehensive error handling.
For email testing, it uses sohamratwadkar@gmail.com as requested.

Usage:
    python test_endpoints.py

Requirements:
    - Backend server running on http://localhost:8000
    - Valid user authentication (will test both scenarios)
    - Gmail API access configured (for email sending tests)
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "sohamratwadkar@gmail.com"
TEST_USER_CREDENTIALS = {
    "username": "testuser",
    "password": "testpass123"
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.current_session_id = None
        self.current_draft_id = None
        
    def log(self, message, color=Colors.WHITE):
        """Log a message with color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.END}")
        
    def log_success(self, message):
        self.log(f"✅ {message}", Colors.GREEN)
        
    def log_error(self, message):
        self.log(f"❌ {message}", Colors.RED)
        
    def log_warning(self, message):
        self.log(f"⚠️  {message}", Colors.YELLOW)
        
    def log_info(self, message):
        self.log(f"ℹ️  {message}", Colors.BLUE)

    def test_endpoint(self, name, method, url, data=None, expected_status=200, auth_required=True):
        """Test a single endpoint with comprehensive error handling"""
        self.log_info(f"Testing {name}...")
        
        try:
            # Make the request
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            elif method.upper() == 'OPTIONS':
                response = self.session.options(url)
            else:
                self.log_error(f"Unsupported HTTP method: {method}")
                return False
                
            # Log request details
            self.log_info(f"Request: {method} {url}")
            if data:
                self.log_info(f"Payload: {json.dumps(data, indent=2)}")
                
            # Log response details
            self.log_info(f"Response Status: {response.status_code}")
            
            try:
                response_data = response.json()
                self.log_info(f"Response Body: {json.dumps(response_data, indent=2)}")
            except:
                self.log_info(f"Response Body (text): {response.text[:200]}...")
                response_data = {}
            
            # Check status code
            if response.status_code == expected_status:
                self.log_success(f"{name} - Status code matches expected ({expected_status})")
                
                # Store useful data for subsequent tests
                if 'session_id' in response_data:
                    self.current_session_id = response_data['session_id']
                    self.log_info(f"Stored session_id: {self.current_session_id}")
                    
                if 'draft_id' in response_data:
                    self.current_draft_id = response_data['draft_id']
                    self.log_info(f"Stored draft_id: {self.current_draft_id}")
                    
                # Check for metadata with draft_id
                if 'message' in response_data and 'metadata' in response_data['message']:
                    metadata = response_data['message']['metadata']
                    if 'draft_id' in metadata:
                        self.current_draft_id = metadata['draft_id']
                        self.log_info(f"Stored draft_id from metadata: {self.current_draft_id}")
                
                self.test_results.append({
                    'test': name,
                    'status': 'PASS',
                    'response_code': response.status_code,
                    'response_data': response_data
                })
                return True
            else:
                self.log_error(f"{name} - Expected {expected_status}, got {response.status_code}")
                self.test_results.append({
                    'test': name,
                    'status': 'FAIL',
                    'response_code': response.status_code,
                    'response_data': response_data,
                    'error': f"Status code mismatch"
                })
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_error(f"{name} - Connection failed. Is the server running on {BASE_URL}?")
            self.test_results.append({
                'test': name,
                'status': 'FAIL',
                'error': 'Connection failed'
            })
            return False
        except Exception as e:
            self.log_error(f"{name} - Unexpected error: {str(e)}")
            self.test_results.append({
                'test': name,
                'status': 'FAIL',
                'error': str(e)
            })
            return False

    def test_server_health(self):
        """Test if the server is running"""
        self.log(f"\n{Colors.BOLD}=== SERVER HEALTH CHECK ==={Colors.END}")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            self.log_success(f"Server is running (Status: {response.status_code})")
            return True
        except:
            self.log_error("Server is not responding. Please start the Django server.")
            return False

    def test_authentication_endpoints(self):
        """Test authentication-related endpoints"""
        self.log(f"\n{Colors.BOLD}=== AUTHENTICATION ENDPOINTS ==={Colors.END}")
        
        # Test user registration (might fail if user exists)
        self.test_endpoint(
            "User Registration",
            "POST",
            f"{BASE_URL}/auth/register/",
            data=TEST_USER_CREDENTIALS,
            expected_status=201  # or 400 if user exists
        )
        
        # Test user login
        login_success = self.test_endpoint(
            "User Login",
            "POST", 
            f"{BASE_URL}/auth/login/",
            data=TEST_USER_CREDENTIALS,
            expected_status=200
        )
        
        if not login_success:
            self.log_warning("Login failed. Some tests may not work without authentication.")
            
        # Test session sync
        self.test_endpoint(
            "Session Sync",
            "GET",
            f"{BASE_URL}/auth/sync-session/",
            expected_status=200
        )

    def test_chat_endpoints(self):
        """Test chat-related endpoints"""
        self.log(f"\n{Colors.BOLD}=== CHAT ENDPOINTS ==={Colors.END}")
        
        # Test starting a chat session
        self.test_endpoint(
            "Start Chat Session",
            "POST",
            f"{BASE_URL}/api/chat/start/",
            data={},
            expected_status=200
        )
        
        # Test sending a general message
        if self.current_session_id:
            self.test_endpoint(
                "Send General Message",
                "POST",
                f"{BASE_URL}/api/chat/send/",
                data={
                    "session_id": self.current_session_id,
                    "message": "Hello, how are you today?"
                },
                expected_status=200
            )
            
            # Test sending an email intent message
            self.test_endpoint(
                "Send Email Intent Message",
                "POST",
                f"{BASE_URL}/api/chat/send/",
                data={
                    "session_id": self.current_session_id,
                    "message": f"Send an email to {TEST_EMAIL} about our meeting tomorrow. Let them know we need to discuss the project timeline and deliverables."
                },
                expected_status=200
            )
            
            # Test getting chat history
            self.test_endpoint(
                "Get Chat History",
                "GET",
                f"{BASE_URL}/api/chat/history/{self.current_session_id}/",
                expected_status=200
            )
        else:
            self.log_warning("No session_id available. Skipping message tests.")

    def test_email_endpoints(self):
        """Test email-related endpoints"""
        self.log(f"\n{Colors.BOLD}=== EMAIL ENDPOINTS ==={Colors.END}")
        
        if not self.current_draft_id:
            self.log_warning("No draft_id available. Creating a test draft first...")
            # Try to create a draft by sending an email intent
            if self.current_session_id:
                self.test_endpoint(
                    "Create Email Draft",
                    "POST",
                    f"{BASE_URL}/api/chat/send/",
                    data={
                        "session_id": self.current_session_id,
                        "message": f"Send a test email to {TEST_EMAIL} with subject 'API Test Email' and body 'This is a test email from the InboxIQ API testing script.'"
                    },
                    expected_status=200
                )
        
        if self.current_draft_id:
            # Test email confirmation - EDIT action
            self.test_endpoint(
                "Email Confirm - Edit Action",
                "POST",
                f"{BASE_URL}/api/email/confirm/",
                data={
                    "draft_id": self.current_draft_id,
                    "action": "edit"
                },
                expected_status=200
            )
            
            # Test email confirmation - CANCEL action
            self.test_endpoint(
                "Email Confirm - Cancel Action",
                "POST",
                f"{BASE_URL}/api/email/confirm/",
                data={
                    "draft_id": self.current_draft_id,
                    "action": "cancel"
                },
                expected_status=200
            )
            
            # Note: We're not testing the SEND action by default to avoid sending actual emails
            # Uncomment the following if you want to test actual email sending:
            """
            self.test_endpoint(
                "Email Confirm - Send Action",
                "POST",
                f"{BASE_URL}/api/email/confirm/",
                data={
                    "draft_id": self.current_draft_id,
                    "action": "send"
                },
                expected_status=200
            )
            """
            self.log_info("Skipping SEND action test to avoid sending actual emails. Uncomment in code to test.")
        else:
            self.log_warning("No draft_id available. Skipping email confirmation tests.")

    def test_error_scenarios(self):
        """Test various error scenarios"""
        self.log(f"\n{Colors.BOLD}=== ERROR SCENARIO TESTS ==={Colors.END}")
        
        # Test invalid JSON
        self.test_endpoint(
            "Invalid JSON Request",
            "POST",
            f"{BASE_URL}/api/chat/send/",
            data="invalid json",
            expected_status=400
        )
        
        # Test missing required fields
        self.test_endpoint(
            "Missing Session ID",
            "POST",
            f"{BASE_URL}/api/chat/send/",
            data={"message": "test"},
            expected_status=400
        )
        
        # Test invalid draft ID
        self.test_endpoint(
            "Invalid Draft ID",
            "POST",
            f"{BASE_URL}/api/email/confirm/",
            data={
                "draft_id": 99999,
                "action": "send"
            },
            expected_status=404
        )
        
        # Test invalid action
        self.test_endpoint(
            "Invalid Action",
            "POST",
            f"{BASE_URL}/api/email/confirm/",
            data={
                "draft_id": 1,
                "action": "invalid_action"
            },
            expected_status=400
        )

    def test_cors_headers(self):
        """Test CORS preflight requests"""
        self.log(f"\n{Colors.BOLD}=== CORS TESTS ==={Colors.END}")
        
        # Test OPTIONS requests
        endpoints = [
            "/api/chat/start/",
            "/api/chat/send/",
            "/api/email/confirm/"
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(
                f"CORS Preflight - {endpoint}",
                "OPTIONS",
                f"{BASE_URL}{endpoint}",
                expected_status=200
            )

    def print_summary(self):
        """Print test results summary"""
        self.log(f"\n{Colors.BOLD}=== TEST RESULTS SUMMARY ==={Colors.END}")
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total Tests: {total_tests}")
        self.log_success(f"Passed: {passed_tests}")
        if failed_tests > 0:
            self.log_error(f"Failed: {failed_tests}")
        else:
            self.log_success("All tests passed! 🎉")
        
        # Print failed tests details
        if failed_tests > 0:
            self.log(f"\n{Colors.BOLD}Failed Tests:{Colors.END}")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    self.log_error(f"- {test['test']}: {test.get('error', 'Unknown error')}")

    def run_all_tests(self):
        """Run all endpoint tests"""
        self.log(f"{Colors.BOLD}{Colors.CYAN}🚀 Starting InboxIQ Backend API Tests{Colors.END}")
        self.log(f"Target Server: {BASE_URL}")
        self.log(f"Test Email: {TEST_EMAIL}")
        self.log(f"Timestamp: {datetime.now().isoformat()}")
        
        # Check if server is running
        if not self.test_server_health():
            self.log_error("Server health check failed. Exiting.")
            return False
        
        # Run test suites
        self.test_authentication_endpoints()
        self.test_chat_endpoints()
        self.test_email_endpoints()
        self.test_error_scenarios()
        self.test_cors_headers()
        
        # Print summary
        self.print_summary()
        
        return len([t for t in self.test_results if t['status'] == 'FAIL']) == 0

def main():
    """Main function to run the tests"""
    tester = APITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        tester.log_warning("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        tester.log_error(f"Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
