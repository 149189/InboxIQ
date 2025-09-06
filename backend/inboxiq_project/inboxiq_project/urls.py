# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Oauth.urls')),
    path('oauth/', include('Oauth.urls')),  # Alternative OAuth path
]
