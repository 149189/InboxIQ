# backend/inboxiq_project/inboxiq_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Oauth.urls')),  # Traditional auth endpoints
    path('api/', include('gmail_agent.urls')),  # Gmail agent API endpoints
    path('api/calendar/', include('calendar_agent.urls')),  # Calendar agent API endpoints
]