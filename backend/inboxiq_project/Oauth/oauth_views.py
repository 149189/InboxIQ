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

        # Clear the state from session
        try:
            request.session.pop('oauth_state', None)
            request.session.save()
        except Exception:
            pass

        # Redirect to frontend with success
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/dashboard?oauth_success=true")

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


@require_GET
def user_profile(request):
    """Get current user profile information"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'profile_picture': user.profile_picture,
        'google_id': user.google_id,
        'is_token_expired': user.is_token_expired(),
        'date_joined': user.date_joined.isoformat()
    })


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
