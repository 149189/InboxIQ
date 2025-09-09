# backend/inboxiq_project/Oauth/session_middleware.py
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse

class CustomSessionMiddleware(SessionMiddleware):
    """
    Custom session middleware to handle session persistence issues with Vite proxy
    """
    
    def process_request(self, request):
        """
        Override to ensure session is properly loaded from cookies
        """
        # Call parent process_request first
        super().process_request(request)
        
        # Debug session loading for auth/API requests
        if request.path.startswith('/auth/') or request.path.startswith('/api/'):
            print(f"[SESSION_MIDDLEWARE] Path: {request.path}")
            print(f"[SESSION_MIDDLEWARE] Session key: {request.session.session_key}")
            print(f"[SESSION_MIDDLEWARE] Session data: {dict(request.session)}")
            print(f"[SESSION_MIDDLEWARE] Cookies: {dict(request.COOKIES)}")
            # Don't access request.user here as auth middleware hasn't run yet
            user_id = request.session.get('_auth_user_id', 'None')
            print(f"[SESSION_MIDDLEWARE] Auth user ID in session: {user_id}")
    
    def process_response(self, request, response):
        """
        Override to ensure session cookies are properly set for cross-origin requests
        """
        response = super().process_response(request, response)
        
        # Apply session cookie handling to both auth and API requests
        if request.path.startswith('/auth/') or request.path.startswith('/api/'):
            # Ensure session cookie is set with proper attributes
            if hasattr(response, 'cookies') and settings.SESSION_COOKIE_NAME in response.cookies:
                cookie = response.cookies[settings.SESSION_COOKIE_NAME]
                
                # Force cookie attributes for development
                if settings.DEBUG:
                    cookie['samesite'] = 'Lax'  # Changed from None to Lax
                    cookie['secure'] = False
                    cookie['httponly'] = False
                    
            # Add explicit CORS headers for all auth/API endpoints
            origin = request.META.get('HTTP_ORIGIN')
            if origin and any(allowed in origin for allowed in ['localhost', '127.0.0.1']):
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Expose-Headers'] = 'Set-Cookie'
                
            # Force session cookie to be sent even if not explicitly set
            if request.session.session_key and not response.cookies.get(settings.SESSION_COOKIE_NAME):
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    path='/',
                    domain=None,
                    secure=False,
                    httponly=False,
                    samesite='Lax'  # Changed from None to Lax
                )
        
        return response