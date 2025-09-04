from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('google/start/', views.google_oauth_start, name='google_start'),
    path('google/callback/', views.google_oauth_callback, name='google_callback'),
]
