from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()


class CalendarSession(models.Model):
    """Calendar session for tracking user interactions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'calendar_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Calendar Session {self.session_id} - {self.user.username}"


class CalendarEvent(models.Model):
    """Model for calendar events"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('tentative', 'Tentative'),
    ]
    
    RECURRENCE_CHOICES = [
        ('none', 'No Recurrence'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    google_event_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Event details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=500, blank=True)
    
    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    all_day = models.BooleanField(default=False)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    recurrence_rule = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    
    # Attendees (stored as JSON)
    attendees = models.JSONField(default=list, blank=True)
    
    # Reminders (stored as JSON)
    reminders = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_events'
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    def add_attendee(self, email, name=None, response_status='needsAction'):
        """Add an attendee to the event"""
        attendee = {
            'email': email,
            'name': name or email.split('@')[0],
            'responseStatus': response_status,
            'added_at': timezone.now().isoformat()
        }
        
        # Check if attendee already exists
        for existing in self.attendees:
            if existing.get('email') == email:
                existing.update(attendee)
                return
        
        self.attendees.append(attendee)
    
    def add_reminder(self, minutes_before, method='popup'):
        """Add a reminder to the event"""
        reminder = {
            'method': method,  # 'popup', 'email'
            'minutes': minutes_before
        }
        
        # Avoid duplicates
        if reminder not in self.reminders:
            self.reminders.append(reminder)
    
    def is_upcoming(self):
        """Check if the event is upcoming"""
        return self.start_datetime > timezone.now()
    
    def duration_minutes(self):
        """Get event duration in minutes"""
        delta = self.end_datetime - self.start_datetime
        return int(delta.total_seconds() / 60)


class CalendarMessage(models.Model):
    """Messages in calendar chat sessions"""
    
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(CalendarSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Metadata for special message types (stored as JSON)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'calendar_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."


class CalendarIntegration(models.Model):
    """User's calendar integration settings"""
    
    PROVIDER_CHOICES = [
        ('google', 'Google Calendar'),
        ('outlook', 'Microsoft Outlook'),
        ('apple', 'Apple Calendar'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='google')
    
    # Integration credentials (encrypted)
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Settings
    default_calendar_id = models.CharField(max_length=255, blank=True)
    sync_enabled = models.BooleanField(default=True)
    auto_create_events = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_integrations'
    
    def __str__(self):
        return f"{self.user.username} - {self.provider} Calendar"
    
    def is_token_valid(self):
        """Check if the access token is still valid"""
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at


class EventTemplate(models.Model):
    """Templates for common event types"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title_template = models.CharField(max_length=255)
    description_template = models.TextField(blank=True)
    default_duration_minutes = models.IntegerField(default=60)
    default_location = models.CharField(max_length=500, blank=True)
    default_reminders = models.JSONField(default=list, blank=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'event_templates'
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
