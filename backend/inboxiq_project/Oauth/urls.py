# backend/inboxiq_project/Oauth/urls.py
from django.urls import path
from .views import register_view, login_view, logout_view
from .oauth_views import (
    google_oauth_login, 
    google_oauth_callback, 
    refresh_google_token, 
    user_profile,
    session_test,
    sync_session,
    update_profile,
    force_login,
    debug_cookies
)

urlpatterns = [
    # Traditional auth endpoints (under /auth/ prefix from main urls.py)
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # OAuth endpoints (under /auth/ prefix from main urls.py)
    # These will be accessible as:
    # /auth/oauth/google/login/
    # /auth/oauth/google/callback/
    # etc.
    path('oauth/google/login/', google_oauth_login, name='google_oauth_login'),
    path('oauth/google/callback/', google_oauth_callback, name='google_oauth_callback'),
    path('oauth/google/refresh/', refresh_google_token, name='refresh_google_token'),
    path('oauth/profile/', user_profile, name='user_profile'),
    path('session-test/', session_test, name='session_test'),
    path('sync-session/', sync_session, name='sync_session'),
    path('update-profile/', update_profile, name='update_profile'),
    path('force-login/', force_login, name='force_login'),
    path('debug-cookies/', debug_cookies, name='debug_cookies'),
]