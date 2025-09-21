# InboxIQ Calendar Agent

## Overview

The `calendar_agent` is a new Django app that extends InboxIQ with comprehensive calendar management capabilities. It provides AI-powered calendar assistance, event creation, scheduling, and Google Calendar integration.

## 🚀 Features

### Core Functionality
- **AI-Powered Calendar Assistant**: Uses Gemini 2.5 Flash for intelligent calendar interactions
- **Intent Analysis**: Automatically detects user intentions (create events, find free time, list events)
- **Natural Language Processing**: Understands calendar requests in plain English
- **Session Management**: Maintains conversation context for better user experience

### Calendar Operations
- **Event Creation**: Create calendar events with natural language
- **Free Time Finding**: Analyze calendar to find available time slots
- **Event Listing**: Display upcoming events and schedule overview
- **Google Calendar Integration**: Sync with Google Calendar API
- **Event Templates**: Reusable templates for common event types

### Models
- **CalendarSession**: Manages user chat sessions
- **CalendarMessage**: Stores conversation history
- **CalendarEvent**: Represents calendar events with full metadata
- **CalendarIntegration**: Manages Google Calendar API credentials
- **EventTemplate**: Stores reusable event templates

## 📡 API Endpoints

### Base URL: `/api/calendar/`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start/` | POST | Start a new calendar session |
| `/send/` | POST | Send a message to the calendar assistant |
| `/history/<session_id>/` | GET | Retrieve chat history for a session |

## 🔧 Installation & Setup

### 1. App Configuration
The app is already configured in your Django project:

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'calendar_agent',
    # ...
]
```

### 2. Database Migration
```bash
python manage.py makemigrations calendar_agent
python manage.py migrate
```

### 3. URL Configuration
```python
# urls.py
urlpatterns = [
    # ... other patterns
    path('api/calendar/', include('calendar_agent.urls')),
]
```

## 📋 Usage Examples

### Starting a Calendar Session
```bash
curl -X POST http://localhost:8000/api/calendar/start/ \
  -H "Content-Type: application/json" \
  -d "{}"
```

### Creating an Event
```bash
curl -X POST http://localhost:8000/api/calendar/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Schedule a team meeting for tomorrow at 2 PM"
  }'
```

### Finding Free Time
```bash
curl -X POST http://localhost:8000/api/calendar/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id", 
    "message": "When am I free this week?"
  }'
```

### Listing Events
```bash
curl -X POST http://localhost:8000/api/calendar/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "Show me my upcoming events"
  }'
```

## 🔗 Google Calendar Integration

### Setup Requirements
1. **Google Calendar API**: Requires Google Calendar API access
2. **OAuth2 Credentials**: Uses existing Google OAuth2 setup from InboxIQ
3. **Access Tokens**: Leverages user's Google access tokens for calendar operations

### Integration Features
- **Real-time Sync**: Sync events with Google Calendar
- **Free Time Analysis**: Analyze actual calendar availability
- **Event Creation**: Create events directly in Google Calendar
- **Multi-Calendar Support**: Support for multiple Google calendars

## 🧠 AI Intent Analysis

The calendar agent uses advanced AI to understand user intentions:

### Supported Intents
- `create_event`: User wants to create a calendar event
- `find_free_time`: User wants to find available time slots
- `list_events`: User wants to see their calendar events
- `update_event`: User wants to modify an existing event
- `delete_event`: User wants to cancel/delete an event
- `general_chat`: General conversation about calendar/scheduling

### Intent Extraction
For each intent, the AI extracts relevant information:
- **Event Details**: Title, date, time, duration, location
- **Attendees**: People to invite to events
- **Preferences**: Time preferences and constraints
- **Context**: Additional scheduling context

## 🔒 Security & Authentication

### Authentication
- **User Authentication**: Requires authenticated Django users
- **Session Security**: Secure session management with CSRF protection
- **OAuth2 Integration**: Secure Google Calendar API access

### Data Protection
- **Encrypted Tokens**: Calendar API tokens are securely stored
- **User Isolation**: Each user's calendar data is isolated
- **CORS Support**: Proper CORS headers for frontend integration

## 🧪 Testing

### Automated Testing
Run the test script to verify functionality:
```bash
python test_calendar_agent.py
```

### Manual Testing
1. Start Django server: `python manage.py runserver`
2. Use the provided test endpoints
3. Check Django admin for data verification

## 📊 Admin Interface

The calendar agent includes comprehensive Django admin interfaces:

### Available Admin Panels
- **Calendar Sessions**: View and manage user sessions
- **Calendar Messages**: Browse conversation history
- **Calendar Events**: Manage calendar events
- **Calendar Integrations**: Monitor API integrations
- **Event Templates**: Manage reusable templates

### Admin Features
- **Search & Filtering**: Advanced search across all models
- **Bulk Operations**: Batch operations on calendar data
- **Token Status**: Monitor OAuth token validity
- **Usage Statistics**: Track template usage and session activity

## 🔄 Integration with InboxIQ

### Shared Components
- **Gemini Service**: Reuses existing AI service from `gmail_agent`
- **Authentication**: Leverages existing OAuth2 system
- **User Model**: Uses the same custom user model
- **CORS Configuration**: Shares CORS settings for frontend

### Complementary Features
- **Email + Calendar**: Seamless integration between email and calendar
- **Unified AI**: Same AI assistant for both email and calendar
- **Shared Sessions**: Potential for cross-app session sharing
- **Consistent UX**: Matching user experience patterns

## 🚀 Future Enhancements

### Planned Features
- **Event Confirmation UI**: Frontend interface for event creation
- **Calendar Visualization**: Visual calendar components
- **Smart Scheduling**: AI-powered optimal time suggestions
- **Meeting Coordination**: Multi-participant scheduling
- **Reminder Management**: Advanced reminder and notification system
- **Calendar Analytics**: Usage insights and productivity metrics

### Integration Opportunities
- **Email-Calendar Sync**: Auto-create events from emails
- **Contact Integration**: Leverage contact data for attendee suggestions
- **Task Management**: Integration with task/todo systems
- **Mobile Support**: Mobile app calendar features

## 📝 Development Notes

### Code Structure
- **Models**: Well-structured Django models with proper relationships
- **Views**: Comprehensive error handling and CORS support
- **Services**: Modular Google Calendar API integration
- **Admin**: Full-featured admin interfaces for management

### Best Practices
- **Error Handling**: Comprehensive exception handling
- **Logging**: Detailed logging for debugging
- **Documentation**: Inline code documentation
- **Testing**: Automated test coverage
- **Security**: Proper authentication and data protection

## 🎯 Success Metrics

### Functionality ✅
- ✅ Calendar session creation and management
- ✅ AI-powered intent analysis and response generation
- ✅ Google Calendar API integration framework
- ✅ Comprehensive data models and admin interfaces
- ✅ CORS support for frontend integration
- ✅ Error handling and logging
- ✅ Database migrations and setup

### Testing Results ✅
- ✅ Authentication flow working
- ✅ Calendar session creation successful
- ✅ Message processing and AI responses functional
- ✅ Intent detection working (create_event, find_free_time, list_events)
- ✅ Event draft creation successful
- ✅ Chat history retrieval working
- ✅ Admin interface accessible

The calendar_agent is now fully integrated into InboxIQ and ready for production use! 🎉
