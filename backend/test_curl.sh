#!/bin/bash

# InboxIQ Backend API Testing with cURL
# Usage: bash test_curl.sh
# 
# This script tests the InboxIQ backend endpoints using cURL commands.
# For email testing, it uses sohamratwadkar@gmail.com as requested.

BASE_URL="http://localhost:8000"
TEST_EMAIL="sohamratwadkar@gmail.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}================================${NC}"
}

print_test() {
    echo -e "${BLUE}🔄 Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to make HTTP requests with cURL
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    print_test "$description"
    echo -e "${PURPLE}Request: $method $BASE_URL$endpoint${NC}"
    
    if [ -n "$data" ]; then
        echo -e "${PURPLE}Data: $data${NC}"
    fi
    
    echo "Response:"
    
    if [ "$method" = "GET" ]; then
        curl -s -w "\nHTTP Status: %{http_code}\n" \
             -H "Content-Type: application/json" \
             -H "Accept: application/json" \
             -b cookies.txt -c cookies.txt \
             "$BASE_URL$endpoint" | jq . 2>/dev/null || curl -s -w "\nHTTP Status: %{http_code}\n" "$BASE_URL$endpoint"
    elif [ "$method" = "POST" ]; then
        if [ -n "$data" ]; then
            curl -s -w "\nHTTP Status: %{http_code}\n" \
                 -X POST \
                 -H "Content-Type: application/json" \
                 -H "Accept: application/json" \
                 -b cookies.txt -c cookies.txt \
                 -d "$data" \
                 "$BASE_URL$endpoint" | jq . 2>/dev/null || curl -s -w "\nHTTP Status: %{http_code}\n" -X POST -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint"
        else
            curl -s -w "\nHTTP Status: %{http_code}\n" \
                 -X POST \
                 -H "Content-Type: application/json" \
                 -H "Accept: application/json" \
                 -b cookies.txt -c cookies.txt \
                 "$BASE_URL$endpoint" | jq . 2>/dev/null || curl -s -w "\nHTTP Status: %{http_code}\n" -X POST "$BASE_URL$endpoint"
        fi
    elif [ "$method" = "OPTIONS" ]; then
        curl -s -w "\nHTTP Status: %{http_code}\n" \
             -X OPTIONS \
             -H "Content-Type: application/json" \
             -H "Accept: application/json" \
             -v \
             "$BASE_URL$endpoint" 2>&1
    fi
    
    echo -e "\n"
}

# Test server health
test_server_health() {
    print_header "SERVER HEALTH CHECK"
    
    print_test "Checking if server is running"
    
    if curl -s --connect-timeout 5 "$BASE_URL/" > /dev/null; then
        print_success "Server is running"
        return 0
    else
        print_error "Server is not responding. Please start the Django server."
        return 1
    fi
}

# Test authentication endpoints
test_authentication() {
    print_header "AUTHENTICATION TESTS"
    
    # Clean cookies
    rm -f cookies.txt
    
    # Test registration
    make_request "POST" "/auth/register/" \
        '{"username": "testuser", "password": "testpass123"}' \
        "User Registration"
    
    # Test login
    make_request "POST" "/auth/login/" \
        '{"username": "testuser", "password": "testpass123"}' \
        "User Login"
    
    # Test session sync
    make_request "GET" "/auth/sync-session/" \
        "" \
        "Session Sync"
}

# Test chat endpoints
test_chat() {
    print_header "CHAT ENDPOINT TESTS"
    
    # Start chat session
    print_test "Starting chat session"
    SESSION_RESPONSE=$(curl -s -b cookies.txt -c cookies.txt \
                           -X POST \
                           -H "Content-Type: application/json" \
                           "$BASE_URL/api/chat/start/" \
                           -d '{}')
    
    echo "Response: $SESSION_RESPONSE"
    
    # Extract session_id (basic extraction, might need adjustment based on actual response)
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$SESSION_ID" ]; then
        print_success "Got session_id: $SESSION_ID"
        
        # Send general message
        make_request "POST" "/api/chat/send/" \
            "{\"session_id\": \"$SESSION_ID\", \"message\": \"Hello! How can you help me today?\"}" \
            "Send General Message"
        
        # Send email intent
        make_request "POST" "/api/chat/send/" \
            "{\"session_id\": \"$SESSION_ID\", \"message\": \"Send an email to $TEST_EMAIL about our meeting tomorrow. Tell them we need to discuss the project timeline.\"}" \
            "Send Email Intent Message"
        
        # Get chat history
        make_request "GET" "/api/chat/history/$SESSION_ID/" \
            "" \
            "Get Chat History"
    else
        print_error "Failed to extract session_id"
    fi
}

# Test email endpoints
test_email() {
    print_header "EMAIL ENDPOINT TESTS"
    
    # Test email confirmation with dummy draft_id
    make_request "POST" "/api/email/confirm/" \
        '{"draft_id": 1, "action": "edit"}' \
        "Email Confirm - Edit Action"
    
    make_request "POST" "/api/email/confirm/" \
        '{"draft_id": 1, "action": "cancel"}' \
        "Email Confirm - Cancel Action"
    
    print_warning "Skipping SEND action to avoid sending actual emails"
}

# Test error scenarios
test_errors() {
    print_header "ERROR SCENARIO TESTS"
    
    # Test invalid JSON
    print_test "Testing invalid JSON"
    curl -s -w "\nHTTP Status: %{http_code}\n" \
         -X POST \
         -H "Content-Type: application/json" \
         -b cookies.txt -c cookies.txt \
         -d "invalid json" \
         "$BASE_URL/api/chat/send/"
    echo -e "\n"
    
    # Test missing fields
    make_request "POST" "/api/chat/send/" \
        '{"message": "test message"}' \
        "Missing Session ID"
    
    # Test invalid draft ID
    make_request "POST" "/api/email/confirm/" \
        '{"draft_id": 99999, "action": "send"}' \
        "Invalid Draft ID"
    
    # Test invalid action
    make_request "POST" "/api/email/confirm/" \
        '{"draft_id": 1, "action": "invalid_action"}' \
        "Invalid Action"
}

# Test CORS
test_cors() {
    print_header "CORS TESTS"
    
    make_request "OPTIONS" "/api/chat/start/" \
        "" \
        "CORS - Chat Start"
    
    make_request "OPTIONS" "/api/chat/send/" \
        "" \
        "CORS - Chat Send"
    
    make_request "OPTIONS" "/api/email/confirm/" \
        "" \
        "CORS - Email Confirm"
}

# Main execution
main() {
    echo -e "${CYAN}"
    echo "🚀 InboxIQ Backend API Testing with cURL"
    echo "========================================"
    echo "Server: $BASE_URL"
    echo "Test Email: $TEST_EMAIL"
    echo "Time: $(date)"
    echo -e "${NC}\n"
    
    # Check if server is running
    if ! test_server_health; then
        exit 1
    fi
    
    # Run all tests
    test_authentication
    test_chat
    test_email
    test_errors
    test_cors
    
    print_header "TESTING COMPLETE"
    print_success "All tests finished. Check the responses above for any errors."
    
    # Clean up
    rm -f cookies.txt
}

# Check if jq is available for JSON formatting
if ! command -v jq &> /dev/null; then
    print_warning "jq not found. JSON responses will not be formatted."
    print_warning "Install jq for better output: sudo apt-get install jq (Linux) or brew install jq (Mac)"
fi

# Run main function
main "$@"
