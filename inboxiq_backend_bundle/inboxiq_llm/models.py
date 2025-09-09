from django.db import models
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # messages stored as JSON array for simplicity
    messages = models.JSONField(default=list)

    def __str__(self):
        return f'Conversation {self.id} (user={self.user_id})'

class Draft(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=512)
    body_html = models.TextField()
    to_emails = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    external_draft_id = models.CharField(max_length=255, blank=True, null=True)  # Gmail draft id

    def __str__(self):
        return f'Draft {self.id} - {self.subject[:60]}'
