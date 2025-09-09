# backend/inboxiq_project/gmail_agent/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class ChatSession(models.Model):
    """Model to store chat sessions for each user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat Session {self.session_id} - {self.user.email}"


class ChatMessage(models.Model):
    """Model to store individual chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Message'),
        ('system', 'System Message'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like email drafts, contacts, etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class EmailDraft(models.Model):
    """Model to store email drafts before sending"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_confirmation', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, null=True, blank=True)
    
    # Email details
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    gmail_draft_id = models.CharField(max_length=255, blank=True, null=True)
    gmail_message_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Contact search metadata
    contact_search_query = models.CharField(max_length=255, blank=True)
    contact_candidates = models.JSONField(default=list, blank=True)  # Store multiple contact matches
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"

    def mark_as_sent(self, gmail_message_id=None):
        """Mark email as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        if gmail_message_id:
            self.gmail_message_id = gmail_message_id
        self.save()


class ContactCache(models.Model):
    """Cache Google Contacts for faster searching"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact_id = models.CharField(max_length=255)  # Google Contact ID
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    
    # Additional contact info
    contact_data = models.JSONField(default=dict)  # Store full contact data from Google
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'contact_id']
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['user', 'email']),
        ]

    def __str__(self):
        return f"{self.name} - {self.email}"