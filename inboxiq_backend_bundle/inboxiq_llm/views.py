import os, json, base64, datetime, redis, requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Conversation, Draft
from auth_app.models import User
from django.views.decorators.http import require_http_methods
from celery import current_app as celery_app

# Redis connection for window buffer
redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

def window_buffer_key(user_id):
    return f"inboxiq:wb:{user_id}"

def push_to_window(user_id, message):
    key = window_buffer_key(user_id)
    redis_client.rpush(key, json.dumps(message))
    # Keep only last 3 messages
    redis_client.ltrim(key, -3, -1)

def get_window(user_id):
    key = window_buffer_key(user_id)
    items = redis_client.lrange(key, 0, -1)
    return [json.loads(i) for i in items]

# Simple Gemini wrapper (placeholder)
def call_gemini(prompt, max_tokens=400):
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        # Return mocked variants for dev/testing
        return [
            {'style':'concise','subject':'Mock: Follow-up','body_html':'<p>Hi — this is a mock concise draft.</p>'},
            {'style':'formal','subject':'Mock: Follow-up (formal)','body_html':'<p>Dear Sir/Madam, this is a mock formal draft.</p>'}
        ]
    # Real call: adapt per Gemini official docs (this is a simplified placeholder)
    url = 'https://api.generativeai.googleapis.com/v1/models/gemini-2.5:generate'
    headers = {'Authorization': f'Bearer {api_key}','Content-Type':'application/json'}
    payload = {'prompt':{'text':prompt}, 'maxOutputTokens': max_tokens}
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        return []
    data = r.json()
    # Extract text result - this depends on the Gemini response shape
    text = data.get('candidates',[{}])[0].get('content',[{}])
    # Simplified parse - wrap into a single variant
    return [{'style':'default','subject':'Draft','body_html': '<p>' + str(data) + '</p>'}]

@csrf_exempt
@require_http_methods(['POST'])
def compose_view(request):
    body = json.loads(request.body)
    user_id = body.get('user_id')
    prompt = body.get('prompt','')
    tone = body.get('tone','concise')
    if not user_id or not prompt:
        return HttpResponseBadRequest('user_id and prompt required')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('invalid user_id')

    # push user message to window buffer
    push_to_window(user_id, {'role':'user','content':prompt})

    # build prompt with window context
    window = get_window(user_id)
    combined = '\n'.join([f"{m['role']}: {m['content']}" for m in window]) + '\nAssistant: please draft email variants in different tones.'
    variants = call_gemini(combined)

    # Save conversation record
    conv = Conversation.objects.create(user=user, messages=window)
    drafts = []
    for v in variants:
        d = Draft.objects.create(user=user, subject=v.get('subject','Draft'), body_html=v.get('body_html',''), to_emails=[])
        drafts.append({'id':d.id,'subject':d.subject,'body_html':d.body_html,'style':v.get('style')})

    return JsonResponse({'drafts':drafts})

# Contacts lookup using Google People API (requires stored tokens)
@csrf_exempt
@require_http_methods(['POST'])
def contacts_lookup(request):
    body = json.loads(request.body)
    user_id = body.get('user_id')
    name = body.get('name','')
    if not user_id or not name:
        return HttpResponseBadRequest('user_id and name required')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('invalid user_id')
    if not user.google_refresh_token:
        return JsonResponse({'candidates':[]})
    # Exchange refresh token for access token
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'refresh_token': user.google_refresh_token,
        'grant_type': 'refresh_token'
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return JsonResponse({'candidates':[]})
    access = r.json().get('access_token')
    # call People API to search
    headers = {'Authorization': f'Bearer {access}'}
    params = {'resourceName':'people/me','personFields':'names,emailAddresses'}
    people_url = 'https://people.googleapis.com/v1/people:searchContacts'
    payload = {'query': name, 'pageSize': 5}
    r2 = requests.post(people_url, headers=headers, json=payload)
    if r2.status_code != 200:
        return JsonResponse({'candidates':[]})
    results = r2.json().get('results', [])
    candidates = []
    for item in results:
        person = item.get('person',{})
        names = person.get('names',[])
        emails = person.get('emailAddresses',[])
        candidates.append({'name': names[0].get('displayName') if names else '', 'emails':[e.get('value') for e in emails]})
    return JsonResponse({'candidates':candidates})

# Enqueue a Celery task to save draft to Gmail (creates draft in Gmail with given body)
@csrf_exempt
@require_http_methods(['POST'])
def save_draft_view(request):
    body = json.loads(request.body)
    user_id = body.get('user_id')
    draft = body.get('draft')
    if not user_id or not draft:
        return HttpResponseBadRequest('user_id and draft required')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('invalid user_id')
    # store draft locally first
    d = Draft.objects.create(user=user, subject=draft.get('subject',''), body_html=draft.get('body_html',''), to_emails=draft.get('to',[]))
    # enqueue Celery task
    try:
        from .tasks import save_draft_to_gmail
        save_draft_to_gmail.delay(d.id)
    except Exception as e:
        return JsonResponse({'status':'queued_failed','error':str(e)})
    return JsonResponse({'status':'queued','draft_id':d.id})
