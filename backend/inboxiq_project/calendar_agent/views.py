# backend/inboxiq_project/calendar_agent/views.py

import json
import uuid
import traceback
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import CalendarSession, CalendarMessage, CalendarEvent, CalendarIntegration
from .google_calendar_service import GoogleCalendarService, GoogleCalendarServiceError
from gmail_agent.gemini_service import GeminiService  # Reuse Gemini service


def _cors_response(resp):
    """Add CORS headers to response"""
    resp['Access-Control-Allow-Origin'] = '*'
    resp['Access-Control-Allow-Credentials'] = 'true'
    return resp


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def start_calendar_session(request):
    """Start a new calendar session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        print(f"[START_CALENDAR] User authenticated: {request.user.is_authenticated}")
        
        if not request.user.is_authenticated:
            response = JsonResponse({'error': 'Not authenticated'}, status=401)
            return _cors_response(response)

        session_id = str(uuid.uuid4())
        calendar_session = CalendarSession.objects.create(
            user=request.user, 
            session_id=session_id
        )

        welcome_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content="Hello! I'm your InboxIQ Calendar Assistant. I can help you create events, schedule meetings, find free time, and manage your calendar. What would you like to do?"
        )

        response_data = {
            'session_id': session_id,
            'message': {
                'id': welcome_message.id,
                'type': 'assistant',
                'content': welcome_message.content,
                'timestamp': welcome_message.timestamp.isoformat()
            }
        }

        response = JsonResponse(response_data)
        return _cors_response(response)

    except Exception as e:
        print(f"[START_CALENDAR] Error: {e}")
        traceback.print_exc()
        response = JsonResponse({'error': str(e)}, status=500)
        return _cors_response(response)


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def send_calendar_message(request):
    """Send a message in a calendar session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        if not request.user.is_authenticated:
            response = JsonResponse({'error': 'Not authenticated'}, status=401)
            return _cors_response(response)

        # Parse request data
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError as e:
            response = JsonResponse({
                'error': 'Invalid JSON in request body',
                'code': 'INVALID_JSON'
            }, status=400)
            return _cors_response(response)

        session_id = data.get('session_id')
        message_content = data.get('message', '').strip()

        if not session_id or not message_content:
            response = JsonResponse({
                'error': 'Session ID and message are required',
                'code': 'MISSING_REQUIRED_FIELDS'
            }, status=400)
            return _cors_response(response)

        calendar_session = get_object_or_404(CalendarSession, session_id=session_id, user=request.user)

        # Create user message
        user_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='user',
            content=message_content
        )

        # Initialize Gemini service
        try:
            gemini_service = GeminiService(use_mock=True)
        except Exception as e:
            print(f"[CALENDAR_MESSAGE] Error initializing Gemini: {e}")
            response = JsonResponse({
                'message': {
                    'id': None,
                    'type': 'assistant',
                    'content': f"I'm having trouble initializing the AI service: {str(e)}. Please try again.",
                    'timestamp': None
                }
            })
            return _cors_response(response)

        # Analyze calendar intent
        try:
            calendar_intent = analyze_calendar_intent(message_content, gemini_service)
            print(f"[CALENDAR_MESSAGE] Intent analysis: {calendar_intent}")
        except Exception as e:
            print(f"[CALENDAR_MESSAGE] Error analyzing intent: {e}")
            response = JsonResponse({
                'message': {
                    'id': None,
                    'type': 'assistant',
                    'content': f"I'm having trouble analyzing your message: {str(e)}. Please try again.",
                    'timestamp': None
                }
            })
            return _cors_response(response)

        # Handle different calendar intents
        if calendar_intent.get('intent') == 'create_event':
            response_data = handle_create_event_intent(request.user, calendar_session, calendar_intent, gemini_service)
        elif calendar_intent.get('intent') == 'find_free_time':
            response_data = handle_find_free_time_intent(request.user, calendar_session, calendar_intent, gemini_service)
        elif calendar_intent.get('intent') == 'list_events':
            response_data = handle_list_events_intent(request.user, calendar_session, calendar_intent, gemini_service)
        else:
            response_data = handle_general_calendar_chat(calendar_session, message_content, gemini_service)

        calendar_session.save()
        response = JsonResponse(response_data)
        return _cors_response(response)

    except Exception as e:
        print(f"[CALENDAR_MESSAGE] Error: {e}")
        traceback.print_exc()
        response = JsonResponse({'error': str(e)}, status=500)
        return _cors_response(response)


def analyze_calendar_intent(message: str, gemini_service) -> dict:
    """Analyze user message for calendar-related intents"""
    
    calendar_prompt = f"""
    Analyze this message for calendar-related intent:
    "{message}"
    
    Determine the intent and extract relevant information:
    
    Possible intents:
    - create_event: User wants to create a calendar event
    - find_free_time: User wants to find available time slots
    - list_events: User wants to see their calendar events
    - update_event: User wants to modify an existing event
    - delete_event: User wants to cancel/delete an event
    - general_chat: General conversation about calendar/scheduling
    
    For create_event, extract:
    - title: Event title/subject
    - date: Date mentioned (if any)
    - time: Time mentioned (if any)
    - duration: Duration mentioned (if any)
    - location: Location mentioned (if any)
    - attendees: People mentioned to invite
    - description: Additional details
    
    For find_free_time, extract:
    - duration: How long they need
    - date_range: When they're looking for time
    - preferences: Any time preferences
    
    Return JSON format:
    {{
        "intent": "intent_name",
        "confidence": 0.0-1.0,
        "extracted_info": {{
            "title": "...",
            "date": "...",
            "time": "...",
            "duration": "...",
            "location": "...",
            "attendees": [...],
            "description": "..."
        }}
    }}
    """
    
    try:
        # Use Gemini to analyze the intent
        response = gemini_service.generate_chat_response(calendar_prompt, [])
        
        # Try to parse JSON response
        try:
            intent_data = json.loads(response)
            return intent_data
        except json.JSONDecodeError:
            # Fallback: simple keyword matching
            return _fallback_intent_analysis(message)
            
    except Exception as e:
        print(f"Error in calendar intent analysis: {e}")
        return _fallback_intent_analysis(message)


def _fallback_intent_analysis(message: str) -> dict:
    """Fallback intent analysis using simple keyword matching"""
    
    message_lower = message.lower()
    
    # Check for specific phrases first (more specific matches)
    
    # Find free time keywords (check first as they're more specific)
    if any(phrase in message_lower for phrase in [
        'when am i free', 'when can i', 'free time', 'available time', 
        'find time', 'when do i have time', 'free this week', 'free today',
        'available this week', 'available today'
    ]):
        return {
            'intent': 'find_free_time',
            'confidence': 0.8,
            'extracted_info': {}
        }
    
    # List events keywords (check second)
    if any(phrase in message_lower for phrase in [
        'show me my', 'show my', 'list my', 'what do i have', 'my calendar',
        'my events', 'upcoming events', 'my schedule', 'what\'s on my calendar',
        'show me upcoming', 'list events'
    ]):
        return {
            'intent': 'list_events',
            'confidence': 0.8,
            'extracted_info': {}
        }
    
    # Create event keywords (check last as they're more general)
    if any(word in message_lower for word in [
        'schedule', 'create', 'book', 'add', 'meeting', 'appointment', 'event'
    ]) and not any(phrase in message_lower for phrase in [
        'show', 'list', 'what do i have', 'my calendar', 'free', 'available'
    ]):
        return {
            'intent': 'create_event',
            'confidence': 0.7,
            'extracted_info': {
                'title': 'New Event',
                'description': message
            }
        }
    
    # Default to general chat
    return {
        'intent': 'general_chat',
        'confidence': 0.5,
        'extracted_info': {}
    }


def handle_create_event_intent(user, calendar_session, intent_data, gemini_service):
    """Handle create event intent"""
    try:
        extracted_info = intent_data.get('extracted_info', {})
        
        # Create a draft event
        event_title = extracted_info.get('title', 'New Event')
        event_description = extracted_info.get('description', '')
        
        # For now, create a draft event in our database
        # In a full implementation, you'd parse dates/times and create actual calendar events
        
        response_content = f"I'll help you create an event: '{event_title}'"
        
        if event_description:
            response_content += f"\n\nDescription: {event_description}"
        
        response_content += "\n\nTo complete the event creation, I'll need:"
        response_content += "\n• Date and time"
        response_content += "\n• Duration (if not specified)"
        response_content += "\n• Location (optional)"
        response_content += "\n• Attendees (optional)"
        
        response_content += "\n\nPlease provide these details, or I can suggest some options."

        assistant_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content=response_content,
            metadata={
                'type': 'event_draft',
                'event_info': extracted_info
            }
        )

        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': response_content,
                'timestamp': assistant_message.timestamp.isoformat(),
                'metadata': {
                    'type': 'event_draft',
                    'event_info': extracted_info
                }
            }
        }

    except Exception as e:
        print(f"Error handling create event intent: {e}")
        return handle_general_calendar_chat(calendar_session, "I'd like to create an event", gemini_service)


def handle_find_free_time_intent(user, calendar_session, intent_data, gemini_service):
    """Handle find free time intent"""
    try:
        # Check if user has calendar integration
        try:
            calendar_integration = CalendarIntegration.objects.get(user=user)
            if not calendar_integration.is_token_valid():
                raise CalendarIntegration.DoesNotExist()
        except CalendarIntegration.DoesNotExist:
            response_content = "To find your free time, I need access to your Google Calendar. Please connect your calendar first."
            
            assistant_message = CalendarMessage.objects.create(
                session=calendar_session,
                message_type='assistant',
                content=response_content
            )
            
            return {
                'message': {
                    'id': assistant_message.id,
                    'type': 'assistant',
                    'content': response_content,
                    'timestamp': assistant_message.timestamp.isoformat()
                }
            }
        
        # If we have calendar access, find free time
        try:
            calendar_service = GoogleCalendarService(calendar_integration.access_token)
            
            # Get free time for the next week (simplified)
            start_date = timezone.now()
            end_date = start_date + timedelta(days=7)
            
            free_slots = calendar_service.find_free_time(
                duration_minutes=60,  # Default 1 hour
                start_date=start_date,
                end_date=end_date
            )
            
            if free_slots:
                response_content = "Here are some available time slots:\n\n"
                for i, slot in enumerate(free_slots[:5]):  # Show first 5 slots
                    start_time = datetime.fromisoformat(slot['start_datetime'].replace('Z', '+00:00'))
                    response_content += f"{i+1}. {start_time.strftime('%A, %B %d at %I:%M %p')}\n"
                
                response_content += "\nWould you like to schedule something in one of these slots?"
            else:
                response_content = "I couldn't find any free time slots in the next week. Your calendar looks quite busy!"
            
        except Exception as e:
            print(f"Error finding free time: {e}")
            response_content = f"I encountered an error while checking your calendar: {str(e)}"

        assistant_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content=response_content
        )

        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': response_content,
                'timestamp': assistant_message.timestamp.isoformat()
            }
        }

    except Exception as e:
        print(f"Error handling find free time intent: {e}")
        return handle_general_calendar_chat(calendar_session, "When am I free?", gemini_service)


def handle_list_events_intent(user, calendar_session, intent_data, gemini_service):
    """Handle list events intent"""
    try:
        # Check if user has calendar integration
        try:
            calendar_integration = CalendarIntegration.objects.get(user=user)
            if not calendar_integration.is_token_valid():
                raise CalendarIntegration.DoesNotExist()
        except CalendarIntegration.DoesNotExist:
            response_content = "To show your calendar events, I need access to your Google Calendar. Please connect your calendar first."
            
            assistant_message = CalendarMessage.objects.create(
                session=calendar_session,
                message_type='assistant',
                content=response_content
            )
            
            return {
                'message': {
                    'id': assistant_message.id,
                    'type': 'assistant',
                    'content': response_content,
                    'timestamp': assistant_message.timestamp.isoformat()
                }
            }
        
        # Get upcoming events
        try:
            calendar_service = GoogleCalendarService(calendar_integration.access_token)
            
            # Get events for the next week
            start_date = timezone.now()
            end_date = start_date + timedelta(days=7)
            
            events = calendar_service.get_events(
                start_date=start_date,
                end_date=end_date,
                max_results=10
            )
            
            if events:
                response_content = "Here are your upcoming events:\n\n"
                for i, event in enumerate(events):
                    start_time = datetime.fromisoformat(event['start_datetime'].replace('Z', '+00:00'))
                    response_content += f"{i+1}. **{event['title']}**\n"
                    response_content += f"   {start_time.strftime('%A, %B %d at %I:%M %p')}\n"
                    if event.get('location'):
                        response_content += f"   📍 {event['location']}\n"
                    response_content += "\n"
            else:
                response_content = "You don't have any events scheduled for the next week. Your calendar is free!"
            
        except Exception as e:
            print(f"Error listing events: {e}")
            response_content = f"I encountered an error while checking your calendar: {str(e)}"

        assistant_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content=response_content
        )

        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': response_content,
                'timestamp': assistant_message.timestamp.isoformat()
            }
        }

    except Exception as e:
        print(f"Error handling list events intent: {e}")
        return handle_general_calendar_chat(calendar_session, "Show my calendar", gemini_service)


def handle_general_calendar_chat(calendar_session, message_content, gemini_service):
    """Handle general calendar conversation"""
    try:
        recent_messages = CalendarMessage.objects.filter(session=calendar_session).order_by('-timestamp')[:10]
        chat_history = [{'message_type': msg.message_type, 'content': msg.content} for msg in reversed(recent_messages)]

        # Create calendar-specific prompt
        calendar_prompt = f"""
        You are InboxIQ's Calendar Assistant. Help the user with calendar and scheduling related tasks.
        
        You can help with:
        - Creating calendar events and meetings
        - Finding free time slots
        - Scheduling appointments
        - Managing calendar conflicts
        - Setting reminders
        - Coordinating with others
        
        User message: {message_content}
        
        Provide a helpful response about calendar management.
        """

        response_content = gemini_service.generate_chat_response(calendar_prompt, chat_history)

        assistant_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content=response_content
        )

        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': response_content,
                'timestamp': assistant_message.timestamp.isoformat()
            }
        }

    except Exception as e:
        print(f"Error handling general calendar chat: {e}")
        
        assistant_message = CalendarMessage.objects.create(
            session=calendar_session,
            message_type='assistant',
            content="I'm sorry, I encountered an error processing your message. Please try again."
        )
        
        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': "I'm sorry, I encountered an error processing your message. Please try again.",
                'timestamp': assistant_message.timestamp.isoformat()
            }
        }


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def get_calendar_history(request, session_id):
    """Get calendar chat history for a session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        if not request.user.is_authenticated:
            response = JsonResponse({'error': 'Not authenticated'}, status=401)
            return _cors_response(response)

        calendar_session = get_object_or_404(CalendarSession, session_id=session_id, user=request.user)
        messages = CalendarMessage.objects.filter(session=calendar_session).order_by('timestamp')

        message_list = [
            {
                'id': msg.id,
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata
            }
            for msg in messages
        ]

        response = JsonResponse({
            'session_id': session_id,
            'messages': message_list
        })
        return _cors_response(response)

    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        return _cors_response(response)
