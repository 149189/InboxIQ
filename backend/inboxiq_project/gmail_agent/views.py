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


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def confirm_email(request):
    """Confirm and send an email draft"""
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
        draft_id = data.get('draft_id')
        action = data.get('action')  # 'send', 'edit', 'cancel'

        if not draft_id:
            return JsonResponse({'error': 'Draft ID is required'}, status=400)

        email_draft = get_object_or_404(EmailDraft, id=draft_id, user=request.user)

        if action == 'send':
            if getattr(request.user, 'access_token', None):
                gmail_service = GmailService(request.user.access_token)
                message_id = gmail_service.send_email_directly(
                    to_email=email_draft.recipient_email,
                    subject=email_draft.subject,
                    body=email_draft.body
                )
                if message_id:
                    email_draft.mark_as_sent(message_id)
                    return JsonResponse({
                        'success': True,
                        'message': f'Email sent successfully to {email_draft.recipient_name}!',
                        'message_id': message_id
                    })
                else:
                    return JsonResponse({'error': 'Failed to send email'}, status=500)
            else:
                return JsonResponse({'error': 'No Gmail access token available'}, status=400)

        elif action == 'edit':
            return JsonResponse({
                'draft': {
                    'id': email_draft.id,
                    'recipient_name': email_draft.recipient_name,
                    'recipient_email': email_draft.recipient_email,
                    'subject': email_draft.subject,
                    'body': email_draft.body
                }
            })

        elif action == 'cancel':
            email_draft.status = 'cancelled'
            email_draft.save()
            return JsonResponse({'success': True, 'message': 'Email draft cancelled'})

        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    except Exception as e:
        print(f"Error in confirm_email: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


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
