from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Additional profile fields
    display_name = models.CharField(max_length=255, blank=True)
    # Google OAuth tokens stored encrypted in prod; plain for dev
    google_refresh_token = models.TextField(blank=True, null=True)
    google_access_token = models.TextField(blank=True, null=True)
    google_token_expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username or self.email
