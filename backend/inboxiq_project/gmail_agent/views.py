# backend/inboxiq_project/gmail_agent/views.py
import json
import uuid
import re
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import ChatSession, ChatMessage, EmailDraft, ContactCache
from .gemini_service import GeminiService
from .contacts_service import GoogleContactsService
from .gmail_service import GmailService

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


def _cors_response(resp):
    resp['Access-Control-Allow-Origin'] = '*'
    resp['Access-Control-Allow-Credentials'] = 'true'
    return resp


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def start_chat_session(request):
    """Start a new chat session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        print(f"[START_CHAT] User authenticated: {request.user.is_authenticated}")
        print(f"[START_CHAT] Session key: {request.session.session_key}")
        print(f"[START_CHAT] Session data: {dict(request.session)}")
        print(f"[START_CHAT] Cookies: {dict(request.COOKIES)}")

        if not request.user.is_authenticated:
            response = JsonResponse({'error': 'Not authenticated'}, status=401)
            _cors_response(response)
            return response

        session_id = str(uuid.uuid4())
        chat_session = ChatSession.objects.create(user=request.user, session_id=session_id)

        welcome_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='assistant',
            content="Hello! I'm InboxIQ, your intelligent email assistant. I can help you with general questions or compose and send emails. How can I assist you today?"
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
        _cors_response(response)
        return response

    except Exception as e:
        print(f"[START_CHAT] Error: {e}")
        traceback.print_exc()
        response = JsonResponse({'error': str(e)}, status=500)
        _cors_response(response)
        return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def send_message(request):
    """Send a message in a chat session"""
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
            _cors_response(response)
            return response

        data = json.loads(request.body)
        session_id = data.get('session_id')
        message_content = data.get('message', '').strip()

        if not session_id or not message_content:
            return JsonResponse({'error': 'Session ID and message are required'}, status=400)

        chat_session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)

        user_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=message_content
        )

        # Initialize Gemini (mock by default)
        try:
            print(f"[SEND_MESSAGE] Initializing Gemini service...")
            gemini_service = GeminiService(use_mock=True)
            print(f"[SEND_MESSAGE] Gemini service initialized successfully")
        except Exception as e:
            print(f"[SEND_MESSAGE] Error initializing Gemini service: {e}")
            traceback.print_exc()
            return JsonResponse({
                'message': {
                    'id': None,
                    'type': 'assistant',
                    'content': f"I'm having trouble initializing the AI service: {str(e)}. Please try again.",
                    'timestamp': None
                }
            })

        # Analyze intent
        try:
            print(f"[SEND_MESSAGE] Analyzing message: {message_content}")
            intent_analysis = gemini_service.analyze_user_intent(message_content)
            print(f"[SEND_MESSAGE] Intent analysis result: {intent_analysis}")
        except Exception as e:
            print(f"[SEND_MESSAGE] Error analyzing intent: {e}")
            traceback.print_exc()
            return JsonResponse({
                'message': {
                    'id': None,
                    'type': 'assistant',
                    'content': f"I'm having trouble analyzing your message: {str(e)}. Please try again.",
                    'timestamp': None
                }
            })

        if intent_analysis.get('intent') == 'email' and intent_analysis.get('confidence', 0) > 0.65:
            response_data = handle_email_intent(request.user, chat_session, intent_analysis, gemini_service)
        else:
            response_data = handle_chat_intent(chat_session, message_content, gemini_service)

        chat_session.save()

        response = JsonResponse(response_data)
        _cors_response(response)
        return response

    except Exception as e:
        print(f"Error in send_message: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


def handle_chat_intent(chat_session, message_content, gemini_service):
    """Handle normal chat conversation"""
    try:
        recent_messages = ChatMessage.objects.filter(session=chat_session).order_by('-timestamp')[:10]
        chat_history = [{'message_type': msg.message_type, 'content': msg.content} for msg in reversed(recent_messages)]

        response_content = gemini_service.generate_chat_response(message_content, chat_history)

        assistant_message = ChatMessage.objects.create(
            session=chat_session,
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
        print(f"Error handling chat intent: {e}")
        traceback.print_exc()
        return {
            'message': {
                'id': None,
                'type': 'assistant',
                'content': "I'm sorry, I encountered an error processing your message. Please try again.",
                'timestamp': None
            }
        }


def handle_email_intent(user, chat_session, intent_analysis, gemini_service):
    """Handle email composition intent"""
    try:
        recipient_info = intent_analysis.get('recipient_info')
        email_context = intent_analysis.get('email_context')

        # If recipient_info missing, try heuristic extraction from email_context
        if not recipient_info and email_context:
            m = re.search(r'\b(?:mail|email|message|send to|send)\s+([A-Za-z][A-Za-z\.\-]*(?:\s+[A-Za-z][A-Za-z\.\-]*){0,4})', email_context, re.I)
            if m:
                recipient_info = m.group(1).strip()
                print(f"[EMAIL_INTENT] Heuristic extracted recipient_info: {recipient_info}")
            else:
                # fallback: treat whole context as hint
                recipient_info = email_context

        # If recipient_info looks like a direct email address, skip contact lookup
        if recipient_info and EMAIL_RE.match(recipient_info.strip()):
            recipient_email = recipient_info.strip()
            recipient_name = recipient_email.split('@')[0]
            print(f"[EMAIL_INTENT] Detected direct email address: {recipient_email}")
            email_content = gemini_service.generate_email_content(
                recipient_name=recipient_name,
                recipient_email=recipient_email,
                email_context=email_context,
                user_name=user.first_name or user.username
            )
            email_draft = EmailDraft.objects.create(
                user=user,
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=email_content.get('subject', '') if isinstance(email_content, dict) else '',
                body=email_content.get('body', '') if isinstance(email_content, dict) else str(email_content),
                status='pending_confirmation',
                contact_search_query=recipient_info,
                contact_candidates=[]
            )
            response_content = f"I'll send to **{recipient_email}**. Is that correct?\n\n"
            response_content += f"**Email Subject:** {email_draft.subject}\n\n"
            response_content += f"**Email Preview:**\n{email_draft.body[:200]}...\n\nReply 'yes' to send, 'edit' to modify, or 'cancel'."
            assistant_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='assistant',
                content=response_content,
                metadata={'type': 'email_confirmation', 'draft_id': email_draft.id, 'contact': {'name': recipient_name, 'email': recipient_email}}
            )
            return {
                'message': {
                    'id': assistant_message.id,
                    'type': 'assistant',
                    'content': response_content,
                    'timestamp': assistant_message.timestamp.isoformat(),
                    'metadata': {
                        'type': 'email_confirmation',
                        'draft_id': email_draft.id,
                        'contact': {'name': recipient_name, 'email': recipient_email},
                        'email_preview': {'subject': email_draft.subject, 'body': email_draft.body}
                    }
                }
            }

        # Extract contact search terms
        try:
            search_terms = gemini_service.extract_contact_search_terms(recipient_info)
        except Exception as e:
            print(f"Error extracting search terms: {e}")
            traceback.print_exc()
            search_terms = []

        print(f"[EMAIL_INTENT] recipient_info={recipient_info!r}, search_terms={search_terms!r}, user.access_token={bool(getattr(user, 'access_token', None))}")

        # Search for contacts
        contact_matches = []
        if getattr(user, 'access_token', None) and search_terms:
            try:
                contacts_service = GoogleContactsService(user.access_token)
                contact_matches = contacts_service.search_contacts(user, search_terms)
            except Exception as e:
                print(f"[EMAIL_INTENT] Error during contacts search: {e}")
                traceback.print_exc()
                contact_matches = []
        else:
            contact_matches = []

        if not contact_matches:
            response_content = f"I couldn't find any contacts matching '{recipient_info}'. Could you provide more specific information or the email address directly?"
            assistant_message = ChatMessage.objects.create(
                session=chat_session,
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

        # Use top match
        top_contact = contact_matches[0]
        recipient_name = top_contact.get('display_name') or top_contact.get('primary_email') or ''
        recipient_email = top_contact.get('primary_email')

        email_content = gemini_service.generate_email_content(
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            email_context=email_context,
            user_name=user.first_name or user.username
        )

        email_draft = EmailDraft.objects.create(
            user=user,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=email_content.get('subject', '') if isinstance(email_content, dict) else '',
            body=email_content.get('body', '') if isinstance(email_content, dict) else str(email_content),
            status='pending_confirmation',
            contact_search_query=recipient_info,
            contact_candidates=contact_matches
        )

        response_content = f"I found a contact for '{recipient_info}'. Is this the right person?\n\n"
        response_content += f"**{recipient_name}** ({recipient_email})\n\n"
        response_content += f"**Email Subject:** {email_draft.subject}\n\n"
        response_content += f"**Email Preview:**\n{email_draft.body[:200]}...\n\n"
        response_content += "Reply with 'yes' to send this email, 'no' to see other contacts, or 'edit' to modify the email content."

        assistant_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='assistant',
            content=response_content,
            metadata={
                'type': 'email_confirmation',
                'draft_id': email_draft.id,
                'contact_matches': contact_matches,
                'email_content': email_content
            }
        )

        return {
            'message': {
                'id': assistant_message.id,
                'type': 'assistant',
                'content': response_content,
                'timestamp': assistant_message.timestamp.isoformat(),
                'metadata': {
                    'type': 'email_confirmation',
                    'draft_id': email_draft.id,
                    'contact': {
                        'name': recipient_name,
                        'email': recipient_email,
                        'photo_url': top_contact.get('photo_url', '')
                    },
                    'email_preview': {
                        'subject': email_draft.subject,
                        'body': email_draft.body
                    }
                }
            }
        }

    except Exception as e:
        print(f"Error handling email intent: {e}")
        traceback.print_exc()
        return {
            'message': {
                'id': None,
                'type': 'assistant',
                'content': "I encountered an error while trying to compose your email. Please try again.",
                'timestamp': None
            }
        }
from .gmail_service import GmailService, GmailServiceError


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def confirm_email(request):
    """
    Confirm and send an email draft with comprehensive error handling.
    
    Actions supported:
    - 'send': Send the email via Gmail API
    - 'edit': Return draft details for editing
    - 'cancel': Cancel the email draft
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Cookie'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Main request processing with comprehensive error handling
    try:
        # 1. Authentication check
        try:
            if not request.user or not request.user.is_authenticated:
                print(f"[CONFIRM_EMAIL] Authentication failed - user: {request.user}")
                response = JsonResponse({
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, status=401)
                return _cors_response(response)
        except AttributeError as e:
            print(f"[CONFIRM_EMAIL] User object error: {e}")
            response = JsonResponse({
                'error': 'Invalid user session',
                'code': 'INVALID_SESSION'
            }, status=401)
            return _cors_response(response)

        # 2. Parse and validate request body
        try:
            if not request.body:
                response = JsonResponse({
                    'error': 'Request body is required',
                    'code': 'MISSING_BODY'
                }, status=400)
                return _cors_response(response)
            
            data = json.loads(request.body)
            if not isinstance(data, dict):
                response = JsonResponse({
                    'error': 'Request body must be a JSON object',
                    'code': 'INVALID_JSON_TYPE'
                }, status=400)
                return _cors_response(response)
                
        except json.JSONDecodeError as e:
            print(f"[CONFIRM_EMAIL] JSON decode error: {e}")
            response = JsonResponse({
                'error': 'Invalid JSON format in request body',
                'code': 'INVALID_JSON',
                'details': str(e)
            }, status=400)
            return _cors_response(response)
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Unexpected error parsing request: {e}")
            response = JsonResponse({
                'error': 'Failed to parse request',
                'code': 'PARSE_ERROR',
                'details': str(e)
            }, status=400)
            return _cors_response(response)

        # 3. Extract and validate required parameters
        try:
            draft_id = data.get('draft_id')
            action = data.get('action', '').strip().lower()
            
            print(f"[CONFIRM_EMAIL] Processing request - user_id: {getattr(request.user, 'id', 'unknown')}, action: {action}, draft_id: {draft_id}")
            
            if not draft_id:
                response = JsonResponse({
                    'error': 'Draft ID is required',
                    'code': 'MISSING_DRAFT_ID'
                }, status=400)
                return _cors_response(response)
            
            if not action:
                response = JsonResponse({
                    'error': 'Action is required',
                    'code': 'MISSING_ACTION'
                }, status=400)
                return _cors_response(response)
            
            if action not in ['send', 'edit', 'cancel']:
                response = JsonResponse({
                    'error': f'Invalid action: {action}. Must be one of: send, edit, cancel',
                    'code': 'INVALID_ACTION'
                }, status=400)
                return _cors_response(response)
                
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Error extracting parameters: {e}")
            response = JsonResponse({
                'error': 'Failed to process request parameters',
                'code': 'PARAM_ERROR',
                'details': str(e)
            }, status=400)
            return _cors_response(response)

        # 4. Retrieve and validate email draft
        try:
            email_draft = EmailDraft.objects.get(
                id=draft_id, 
                user=request.user
            )
        except EmailDraft.DoesNotExist:
            print(f"[CONFIRM_EMAIL] Draft not found - draft_id: {draft_id}, user_id: {getattr(request.user, 'id', 'unknown')}")
            response = JsonResponse({
                'error': f'Email draft not found or access denied',
                'code': 'DRAFT_NOT_FOUND',
                'draft_id': draft_id
            }, status=404)
            return _cors_response(response)
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Database error retrieving draft: {e}")
            traceback.print_exc()
            response = JsonResponse({
                'error': 'Database error retrieving email draft',
                'code': 'DB_ERROR',
                'details': str(e)
            }, status=500)
            return _cors_response(response)

        # 5. Process action-specific logic
        if action == 'send':
            return _handle_send_action(request, email_draft, draft_id)
        elif action == 'edit':
            return _handle_edit_action(email_draft)
        elif action == 'cancel':
            return _handle_cancel_action(email_draft, draft_id)

    except Exception as e:
        # Catch-all for any unexpected errors
        print(f"[CONFIRM_EMAIL] Unexpected server error: {e}")
        traceback.print_exc()
        response = JsonResponse({
            'error': 'Internal server error occurred',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if hasattr(e, '__str__') else 'Unknown error'
        }, status=500)
        return _cors_response(response)


def _handle_send_action(request, email_draft, draft_id):
    """Handle the 'send' action with comprehensive error handling."""
    try:
        # Validate user has access token
        try:
            access_token = getattr(request.user, 'access_token', None)
            if not access_token or not isinstance(access_token, str) or not access_token.strip():
                print(f"[CONFIRM_EMAIL] Missing or invalid access token for user {getattr(request.user, 'id', 'unknown')}")
                response = JsonResponse({
                    'error': 'Gmail access token not available. Please reconnect your Google account.',
                    'code': 'NO_ACCESS_TOKEN'
                }, status=400)
                return _cors_response(response)
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Error checking access token: {e}")
            response = JsonResponse({
                'error': 'Failed to validate Gmail access',
                'code': 'TOKEN_CHECK_ERROR',
                'details': str(e)
            }, status=500)
            return _cors_response(response)

        # Validate email draft fields
        try:
            validation_errors = []
            
            if not email_draft.recipient_email or not email_draft.recipient_email.strip():
                validation_errors.append('Recipient email is missing')
            elif not EMAIL_RE.match(email_draft.recipient_email.strip()):
                validation_errors.append('Recipient email format is invalid')
                
            if not email_draft.subject or not email_draft.subject.strip():
                validation_errors.append('Email subject is missing')
                
            if not hasattr(email_draft, 'body') or email_draft.body is None:
                validation_errors.append('Email body is missing')
                
            if validation_errors:
                response = JsonResponse({
                    'error': 'Email draft validation failed',
                    'code': 'VALIDATION_ERROR',
                    'validation_errors': validation_errors
                }, status=400)
                return _cors_response(response)
                
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Error validating email draft: {e}")
            response = JsonResponse({
                'error': 'Failed to validate email draft',
                'code': 'DRAFT_VALIDATION_ERROR',
                'details': str(e)
            }, status=500)
            return _cors_response(response)

        # Initialize Gmail service
        try:
            gmail_service = GmailService(access_token.strip())
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Error initializing Gmail service: {e}")
            traceback.print_exc()
            response = JsonResponse({
                'error': 'Failed to initialize Gmail service. Please check your Google account connection.',
                'code': 'GMAIL_INIT_ERROR',
                'details': str(e)
            }, status=500)
            return _cors_response(response)

        # Send email via Gmail API
        try:
            print(f"[CONFIRM_EMAIL] Attempting to send email - to: {email_draft.recipient_email}, subject: {email_draft.subject[:50]}...")
            
            message_id = gmail_service.send_email_directly(
                to_email=email_draft.recipient_email.strip(),
                subject=email_draft.subject.strip(),
                body=email_draft.body or ''
            )
            
            if not message_id:
                print(f"[CONFIRM_EMAIL] Gmail service returned empty message_id for draft {draft_id}")
                response = JsonResponse({
                    'error': 'Email sending failed - no message ID returned',
                    'code': 'NO_MESSAGE_ID'
                }, status=500)
                return _cors_response(response)
                
        except GmailServiceError as e:
            print(f"[CONFIRM_EMAIL] Gmail API error: {e}")
            traceback.print_exc()
            response = JsonResponse({
                'error': 'Gmail API error occurred while sending email',
                'code': 'GMAIL_API_ERROR',
                'details': str(e)
            }, status=502)
            return _cors_response(response)
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Unexpected error sending email: {e}")
            traceback.print_exc()
            response = JsonResponse({
                'error': 'Unexpected error occurred while sending email',
                'code': 'SEND_ERROR',
                'details': str(e)
            }, status=500)
            return _cors_response(response)

        # Update draft status
        try:
            with transaction.atomic():
                if hasattr(email_draft, 'mark_as_sent') and callable(getattr(email_draft, 'mark_as_sent')):
                    email_draft.mark_as_sent(message_id)
                else:
                    email_draft.status = 'sent'
                    if hasattr(email_draft, 'sent_message_id'):
                        setattr(email_draft, 'sent_message_id', message_id)
                    email_draft.save()
            
            print(f"[CONFIRM_EMAIL] Successfully sent email - draft_id: {draft_id}, message_id: {message_id}")
            
        except Exception as e:
            print(f"[CONFIRM_EMAIL] Error updating draft status: {e}")
            traceback.print_exc()
            # Email was sent successfully, but we couldn't update the status
            response = JsonResponse({
                'success': True,
                'message': f'Email sent successfully, but failed to update status: {str(e)}',
                'message_id': message_id,
                'code': 'SENT_STATUS_UPDATE_FAILED'
            })
            return _cors_response(response)

        # Success response
        response = JsonResponse({
            'success': True,
            'message': f'Email sent successfully to {email_draft.recipient_name or email_draft.recipient_email}!',
            'message_id': message_id,
            'recipient': email_draft.recipient_email
        })
        return _cors_response(response)

    except Exception as e:
        print(f"[CONFIRM_EMAIL] Unexpected error in send action: {e}")
        traceback.print_exc()
        response = JsonResponse({
            'error': 'Unexpected error occurred during send operation',
            'code': 'SEND_OPERATION_ERROR',
            'details': str(e)
        }, status=500)
        return _cors_response(response)


def _handle_edit_action(email_draft):
    """Handle the 'edit' action with error handling."""
    try:
        draft_data = {
            'id': email_draft.id,
            'recipient_name': email_draft.recipient_name or '',
            'recipient_email': email_draft.recipient_email or '',
            'subject': email_draft.subject or '',
            'body': email_draft.body or ''
        }
        
        response = JsonResponse({
            'success': True,
            'draft': draft_data
        })
        return _cors_response(response)
        
    except Exception as e:
        print(f"[CONFIRM_EMAIL] Error in edit action: {e}")
        traceback.print_exc()
        response = JsonResponse({
            'error': 'Failed to retrieve draft for editing',
            'code': 'EDIT_ERROR',
            'details': str(e)
        }, status=500)
        return _cors_response(response)


def _handle_cancel_action(email_draft, draft_id):
    """Handle the 'cancel' action with error handling."""
    try:
        with transaction.atomic():
            email_draft.status = 'cancelled'
            email_draft.save()
        
        print(f"[CONFIRM_EMAIL] Successfully cancelled draft {draft_id}")
        
        response = JsonResponse({
            'success': True,
            'message': 'Email draft cancelled successfully'
        })
        return _cors_response(response)
        
    except Exception as e:
        print(f"[CONFIRM_EMAIL] Error cancelling draft {draft_id}: {e}")
        traceback.print_exc()
        response = JsonResponse({
            'error': 'Failed to cancel email draft',
            'code': 'CANCEL_ERROR',
            'details': str(e)
        }, status=500)
        return _cors_response(response)



@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
@login_required
def get_chat_history(request, session_id):
    """Get chat history for a session"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        chat_session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)

        messages = ChatMessage.objects.filter(session=chat_session).order_by('timestamp')

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

        return JsonResponse({
            'session_id': session_id,
            'messages': message_list
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
@login_required
def get_user_sessions(request):
    """Get all chat sessions for the current user"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response

    try:
        sessions = ChatSession.objects.filter(user=request.user, is_active=True)

        session_list = [
            {
                'session_id': session.session_id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': session.messages.count()
            }
            for session in sessions
        ]

        return JsonResponse({'sessions': session_list})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
