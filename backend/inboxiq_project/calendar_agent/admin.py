from django.contrib import admin
from .models import CalendarSession, CalendarMessage, CalendarEvent, CalendarIntegration, EventTemplate


@admin.register(CalendarSession)
class CalendarSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session_id', 'user__username', 'user__email')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(CalendarMessage)
class CalendarMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'content_preview', 'timestamp')
    list_filter = ('message_type', 'timestamp')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_datetime', 'end_datetime', 'status', 'created_at')
    list_filter = ('status', 'all_day', 'recurrence_rule', 'created_at')
    search_fields = ('title', 'description', 'location', 'user__username')
    readonly_fields = ('google_event_id', 'created_at', 'updated_at')
    ordering = ('-start_datetime',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'location')
        }),
        ('Timing', {
            'fields': ('start_datetime', 'end_datetime', 'timezone', 'all_day', 'recurrence_rule')
        }),
        ('Status & Integration', {
            'fields': ('status', 'google_event_id')
        }),
        ('Attendees & Reminders', {
            'fields': ('attendees', 'reminders'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarIntegration)
class CalendarIntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'sync_enabled', 'token_status', 'created_at')
    list_filter = ('provider', 'sync_enabled', 'auto_create_events')
    search_fields = ('user__username', 'user__email', 'default_calendar_id')
    readonly_fields = ('created_at', 'updated_at', 'token_expires_at')
    
    fieldsets = (
        ('User & Provider', {
            'fields': ('user', 'provider')
        }),
        ('Settings', {
            'fields': ('default_calendar_id', 'sync_enabled', 'auto_create_events')
        }),
        ('Credentials', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',),
            'description': 'Sensitive credential information'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def token_status(self, obj):
        if obj.is_token_valid():
            return "✅ Valid"
        else:
            return "❌ Expired/Invalid"
    token_status.short_description = 'Token Status'


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'default_duration_minutes', 'usage_count', 'created_at')
    list_filter = ('default_duration_minutes', 'created_at')
    search_fields = ('name', 'title_template', 'user__username')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    ordering = ('-usage_count', 'name')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('user', 'name', 'title_template', 'description_template')
        }),
        ('Default Settings', {
            'fields': ('default_duration_minutes', 'default_location', 'default_reminders')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
