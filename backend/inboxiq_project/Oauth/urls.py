# accounts/urls.py
from django.urls import path
from .views import register_view, login_view, logout_view
from .oauth_views import (
    google_oauth_login, 
    google_oauth_callback, 
    refresh_google_token, 
    user_profile
)

urlpatterns = [
    # Traditional auth endpoints
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # OAuth endpoints
    path('oauth/google/login/', google_oauth_login, name='google_oauth_login'),
    path('oauth/google/callback/', google_oauth_callback, name='google_oauth_callback'),
    path('oauth/google/refresh/', refresh_google_token, name='refresh_google_token'),
    path('oauth/profile/', user_profile, name='user_profile'),
]
