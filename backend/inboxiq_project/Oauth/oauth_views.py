# backend/inboxiq_project/Oauth/oauth_views.py
import json
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests

from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from .models import CustomUser


def generate_oauth_url():
    """Generate Google OAuth authorization URL"""
    state = secrets.token_urlsafe(32)

    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
        'scope': ' '.join(settings.GOOGLE_OAUTH_SCOPES),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }

    auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    return auth_url, state


@require_GET
def google_oauth_login(request):
    """
    Start OAuth flow by storing state in the session and issuing a server-side
    redirect to Google's OAuth endpoint. This ensures the session cookie
    (sessionid) is set on the browser in the same response that redirects to Google.
    """
    try:
        auth_url, state = generate_oauth_url()

        # Store state in session for verification
        request.session['oauth_state'] = state
        # Ensure session is written immediately
        request.session.save()

        # Debug: print what's stored and session info
        print(f"[OAUTH START] Stored state={state} session_key={request.session.session_key} session_keys={list(request.session.keys())}")

        # Redirect browser to Google's OAuth consent page
        return redirect(auth_url)
    except Exception as e:
        print(f"[OAUTH START] Error generating auth url: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def google_oauth_callback(request):
    """Handle Google OAuth callback"""
    try:
        # Get authorization code and state from query parameters
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')

        # Debug: show what was received and what is in session/cookies
        stored_state = request.session.get('oauth_state')
        session_key = request.session.session_key
        cookies = dict(request.COOKIES or {})
        print("[OAUTH CALLBACK] received state:", state)
        print("[OAUTH CALLBACK] stored_state (from session):", stored_state)
        print("[OAUTH CALLBACK] session_key:", session_key)
        print("[OAUTH CALLBACK] request.COOKIES keys:", list(cookies.keys()))

        if error:
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error={error}")

        if not code:
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=no_code")

        # Verify state parameter
        if not stored_state or stored_state != state:
            # Debug log for mismatch
            print(f"[OAUTH CALLBACK] state mismatch: stored={stored_state} received={state}")
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=invalid_state")

        # Exchange authorization code for tokens
        token_data = exchange_code_for_tokens(code)
        if not token_data:
            print("[OAUTH CALLBACK] token exchange failed")
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=token_exchange_failed")

        # Get user info from Google
        user_info = get_google_user_info(token_data.get('access_token'))
        if not user_info:
            print("[OAUTH CALLBACK] failed to fetch user info")
            return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=user_info_failed")

        # Create or update user
        user = create_or_update_user(user_info, token_data)

        # Log in the user (creates session auth)
        login(request, user)
        
        # Force session save and ensure it's persistent
        request.session.save()
        
        # Clear the state from session
        try:
            request.session.pop('oauth_state', None)
            request.session.save()
        except Exception:
            pass

        # Create response with explicit session cookie
        response = HttpResponseRedirect(f"{settings.FRONTEND_URL}/chat?oauth_success=true")
        
        # Ensure session cookie is set properly for cross-origin
        if request.session.session_key:
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                request.session.session_key,
                max_age=settings.SESSION_COOKIE_AGE,
                path=settings.SESSION_COOKIE_PATH or '/',
                domain=settings.SESSION_COOKIE_DOMAIN,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                samesite=settings.SESSION_COOKIE_SAMESITE
            )
        
        return response

    except Exception as e:
        print(f"[OAUTH CALLBACK] unexpected error: {e}")
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/login?error=oauth_failed")


def exchange_code_for_tokens(code):
    """Exchange authorization code for access and refresh tokens"""
    try:
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"Token exchange error: {e}")
        return None


def get_google_user_info(access_token):
    """Get user information from Google using access token"""
    try:
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"

        response = requests.get(user_info_url)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        print(f"User info error: {e}")
        return None


def create_or_update_user(user_info, token_data):
    """Create or update user with Google OAuth data"""
    google_id = user_info.get('id')
    email = user_info.get('email')
    first_name = user_info.get('given_name', '')
    last_name = user_info.get('family_name', '')
    profile_picture = user_info.get('picture', '')

    # Calculate token expiration time
    expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
    expires_at = timezone.now() + timedelta(seconds=int(expires_in))

    # Try to find existing user by Google ID
    try:
        user = CustomUser.objects.get(google_id=google_id)
        # Update existing user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.profile_picture = profile_picture
        user.access_token = token_data.get('access_token')
        user.refresh_token = token_data.get('refresh_token', user.refresh_token)
        user.token_expires_at = expires_at
        user.save()
        return user
    except CustomUser.DoesNotExist:
        pass

    # Try to find existing user by email
    if email:
        try:
            user = CustomUser.objects.get(email=email)
            # Link Google account to existing user
            user.google_id = google_id
            user.first_name = first_name or user.first_name
            user.last_name = last_name or user.last_name
            user.profile_picture = profile_picture
            user.access_token = token_data.get('access_token')
            user.refresh_token = token_data.get('refresh_token')
            user.token_expires_at = expires_at
            user.save()
            return user
        except CustomUser.DoesNotExist:
            pass

    # Create new user
    username = email.split('@')[0] if email else f"user_{google_id}"

    # Ensure username is unique
    base_username = username
    counter = 1
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1

    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        google_id=google_id,
        access_token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_expires_at=expires_at,
        profile_picture=profile_picture
    )

    return user


@csrf_exempt
@require_POST
def refresh_google_token(request):
    """Refresh Google OAuth access token"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)

        user = request.user
        if not user.refresh_token:
            return JsonResponse({'error': 'No refresh token available'}, status=400)

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
            'refresh_token': user.refresh_token,
            'grant_type': 'refresh_token',
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        token_data = response.json()

        # Update user tokens
        expires_in = token_data.get('expires_in', 3600)
        expires_at = timezone.now() + timedelta(seconds=int(expires_in))

        user.access_token = token_data.get('access_token')
        user.token_expires_at = expires_at

        # Update refresh token if provided
        if 'refresh_token' in token_data:
            user.refresh_token = token_data['refresh_token']

        user.save()

        return JsonResponse({
            'message': 'Token refreshed successfully',
            'expires_at': expires_at.isoformat()
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def user_profile(request):
    """Get current user profile information"""
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Check authentication
    if not request.user.is_authenticated:
        print(f"[USER_PROFILE] User not authenticated. Session key: {request.session.session_key}")
        print(f"[USER_PROFILE] Session data: {dict(request.session)}")
        print(f"[USER_PROFILE] Cookies: {dict(request.COOKIES)}")
        response = JsonResponse({'error': 'Not authenticated'}, status=401)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    user = request.user
    print(f"[USER_PROFILE] Authenticated user: {user.email}")
    
    response_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'profile_picture': user.profile_picture,
        'google_id': user.google_id,
        'is_token_expired': user.is_token_expired(),
        'date_joined': user.date_joined.isoformat(),
        'name': user.first_name or user.username  # Add name field for frontend compatibility
    }
    
    response = JsonResponse(response_data)
    response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
@login_required
def update_profile(request):
    """Update user profile (username and profile picture)"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Update username if provided
        if 'username' in data and data['username'].strip():
            new_username = data['username'].strip()
            
            # Check if username is already taken by another user
            if CustomUser.objects.filter(username=new_username).exclude(id=user.id).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)
            
            user.username = new_username
        
        # Update display name if provided
        if 'display_name' in data and data['display_name'].strip():
            display_name = data['display_name'].strip()
            # Split display name into first and last name
            name_parts = display_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Update profile picture URL if provided
        if 'profile_picture' in data and data['profile_picture'].strip():
            user.profile_picture = data['profile_picture'].strip()
        
        user.save()
        
        response_data = {
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'display_name': user.full_name,
                'profile_picture': user.profile_picture,
            }
        }
        
        response = JsonResponse(response_data)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# oauth_views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def profile_view(request):
    user = request.user
    return JsonResponse({
        "email": user.email,
        "name": user.first_name or user.username
    })


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def session_test(request):
    """Test endpoint to debug session and authentication issues"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    session_data = {
        'session_key': request.session.session_key,
        'session_data': dict(request.session),
        'cookies': dict(request.COOKIES),
        'user_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
        'user_email': request.user.email if request.user.is_authenticated else None,
        'origin': request.META.get('HTTP_ORIGIN'),
        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
    }
    
    response = JsonResponse(session_data)
    response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
    response['Access-Control-Allow-Credentials'] = 'true'
    return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def sync_session(request):
    """Sync session after OAuth redirect to ensure frontend has proper session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    # Force session creation if it doesn't exist
    if not request.session.session_key:
        request.session.create()
    
    # Debug session information
    print(f"[SYNC_SESSION] Session key: {request.session.session_key}")
    print(f"[SYNC_SESSION] Session data: {dict(request.session)}")
    print(f"[SYNC_SESSION] User authenticated: {request.user.is_authenticated}")
    print(f"[SYNC_SESSION] User ID: {getattr(request.user, 'id', None)}")
    
    # Check if user is authenticated
    if request.user.is_authenticated:
        user = request.user
        response_data = {
            'authenticated': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'profile_picture': user.profile_picture,
            },
            'session_key': request.session.session_key
        }
        print(f"[SYNC_SESSION] User authenticated: {user.email}, session: {request.session.session_key}")
    else:
        # Try to find and authenticate the user if they exist but aren't logged in
        # This is a fallback for when OAuth completed but session wasn't properly saved
        try:
            # Look for the most recent user (assuming this is the one that just completed OAuth)
            user = CustomUser.objects.filter(access_token__isnull=False).order_by('-last_login').first()
            if user:
                print(f"[SYNC_SESSION] Found user {user.email}, attempting to log them in")
                login(request, user)
                request.session.save()
                
                response_data = {
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.first_name or user.username,
                        'profile_picture': user.profile_picture,
                    },
                    'session_key': request.session.session_key
                }
                print(f"[SYNC_SESSION] Successfully logged in user: {user.email}")
            else:
                response_data = {
                    'authenticated': False,
                    'session_key': request.session.session_key
                }
                print(f"[SYNC_SESSION] No user found to authenticate")
        except Exception as e:
            print(f"[SYNC_SESSION] Error trying to authenticate user: {e}")
            response_data = {
                'authenticated': False,
                'session_key': request.session.session_key
            }
    
    response = JsonResponse(response_data)
    response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
    response['Access-Control-Allow-Credentials'] = 'true'
    
    # Ensure session cookie is set properly
    if request.session.session_key:
        response.set_cookie(
            settings.SESSION_COOKIE_NAME,
            request.session.session_key,
            max_age=settings.SESSION_COOKIE_AGE,
            path='/',
            domain=None,
            secure=False,
            httponly=False,
            samesite=None
        )
    
    return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def force_login(request):
    """Force login for debugging - manually authenticate the user"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    try:
        # Find the user with the Google ID from the database
        user = CustomUser.objects.get(google_id='104686034682116627108')
        
        # Log them in
        login(request, user)
        request.session.save()
        
        print(f"[FORCE_LOGIN] Successfully logged in user: {user.email}")
        
        response_data = {
            'success': True,
            'message': 'User logged in successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'profile_picture': user.profile_picture,
            }
        }
        
        response = JsonResponse(response_data)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        print(f"[FORCE_LOGIN] Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def debug_cookies(request):
    """Debug endpoint to check cookies and session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    
    debug_info = {
        'path': request.path,
        'session_key': request.session.session_key,
        'session_data': dict(request.session),
        'cookies': dict(request.COOKIES),
        'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else 'No user attr',
        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
        'headers': {
            'cookie': request.META.get('HTTP_COOKIE', 'No cookie header'),
            'origin': request.META.get('HTTP_ORIGIN', 'No origin'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'No user agent')[:100],
        }
    }
    
    print(f"[DEBUG_COOKIES] {debug_info}")
    
    response = JsonResponse(debug_info)
    response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
    response['Access-Control-Allow-Credentials'] = 'true'
    return response
