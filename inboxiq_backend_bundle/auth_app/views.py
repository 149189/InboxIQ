import os, json, requests, datetime
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User

# Simple username/password registration and login (for dev only)
@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'error':'POST required'}, status=400)
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email','')
    if not username or not password:
        return JsonResponse({'error':'username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error':'username exists'}, status=400)
    u = User.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({'id':u.id, 'username':u.username})

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error':'POST required'}, status=400)
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error':'invalid credentials'}, status=400)
    login(request, user)
    return JsonResponse({'id':user.id, 'username':user.username})

# Google OAuth: start and callback. Uses OAuth 2.0 for web server apps.
def google_oauth_start(request):
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect_uri = os.getenv('GOOGLE_OAUTH_REDIRECT')
    scope = 'https://www.googleapis.com/auth/gmail.compose https://www.googleapis.com/auth/contacts.readonly'
    state = 'inboxiq'  # production: random state per-session
    auth_url = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                f'&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&access_type=offline&prompt=consent&state={state}')
    return redirect(auth_url)

def google_oauth_callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponseBadRequest('missing code')
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.getenv('GOOGLE_OAUTH_REDIRECT'),
        'grant_type': 'authorization_code'
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        return HttpResponseBadRequest('token exchange failed')
    token_info = r.json()
    # For demo: attach tokens to currently logged-in user (or create a mapping)
    # Here we expect a logged-in Django session user; in production tie to user via state
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('login first before connecting Google account (for demo)')
    user = request.user
    user.google_refresh_token = token_info.get('refresh_token') or user.google_refresh_token
    user.google_access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in')
    if expires_in:
        user.google_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(expires_in))
    user.save()
    return JsonResponse({'status':'connected'})
