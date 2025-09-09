# backend/inboxiq_project/Oauth/middleware.py
# Create this file to help debug session issues

import json
from django.conf import settings

class SessionDebugMiddleware:
    """
    Middleware to debug session and CORS issues during development.
    Add this to MIDDLEWARE in settings.py temporarily if you need to debug sessions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only run in DEBUG mode
        if not settings.DEBUG:
            return self.get_response(request)
            
        # Skip static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return self.get_response(request)
            
        # Log incoming request info
        if request.path.startswith('/auth/'):
            print(f"\n[SESSION DEBUG] {request.method} {request.path}")
            print(f"[SESSION DEBUG] Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
            print(f"[SESSION DEBUG] User-Agent: {request.META.get('HTTP_USER_AGENT', 'None')[:100]}...")
            print(f"[SESSION DEBUG] Session key (before): {request.session.session_key}")
            print(f"[SESSION DEBUG] Session data (before): {dict(request.session)}")
            print(f"[SESSION DEBUG] Cookies: {dict(request.COOKIES)}")
            print(f"[SESSION DEBUG] User authenticated (before): {request.user.is_authenticated if hasattr(request, 'user') else 'N/A'}")

        response = self.get_response(request)

        # Log response info
        if request.path.startswith('/auth/'):
            print(f"[SESSION DEBUG] Response status: {response.status_code}")
            print(f"[SESSION DEBUG] Session key (after): {request.session.session_key}")
            print(f"[SESSION DEBUG] Session data (after): {dict(request.session)}")
            print(f"[SESSION DEBUG] User authenticated (after): {request.user.is_authenticated if hasattr(request, 'user') else 'N/A'}")
            
            # Check if session cookie is being set
            if hasattr(response, 'cookies') and 'sessionid' in response.cookies:
                cookie = response.cookies['sessionid']
                print(f"[SESSION DEBUG] Setting session cookie: {cookie.key}={cookie.value[:10]}...")
                print(f"[SESSION DEBUG] Cookie domain: {cookie.get('domain')}")
                print(f"[SESSION DEBUG] Cookie path: {cookie.get('path')}")
                print(f"[SESSION DEBUG] Cookie secure: {cookie.get('secure')}")
                print(f"[SESSION DEBUG] Cookie samesite: {cookie.get('samesite')}")
            print("[SESSION DEBUG] " + "="*50)

        return response


# Add CORS debugging as well
class CorsDebugMiddleware:
    """
    Middleware to debug CORS headers during development.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)
            
        # Log CORS-related headers for API calls
        if request.path.startswith('/auth/'):
            origin = request.META.get('HTTP_ORIGIN')
            if origin:
                print(f"\n[CORS DEBUG] Request from origin: {origin}")
                print(f"[CORS DEBUG] Method: {request.method}")
                print(f"[CORS DEBUG] Path: {request.path}")
                
        response = self.get_response(request)
        
        # Log CORS response headers
        if request.path.startswith('/auth/') and request.META.get('HTTP_ORIGIN'):
            cors_headers = {
                'Access-Control-Allow-Origin': response.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Credentials': response.get('Access-Control-Allow-Credentials'),
                'Access-Control-Allow-Methods': response.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.get('Access-Control-Allow-Headers'),
            }
            print(f"[CORS DEBUG] Response headers: {cors_headers}")
            print("[CORS DEBUG] " + "="*40)
            
        return response