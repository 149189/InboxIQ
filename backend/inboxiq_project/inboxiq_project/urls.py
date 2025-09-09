# backend/inboxiq_project/inboxiq_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Oauth.urls')),  # Traditional auth endpoints
    # Remove the duplicate oauth/ path - it's causing double prefixing
    # path('oauth/', include('Oauth.urls')),  # Remove this line!
]