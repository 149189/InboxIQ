# accounts/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_POST
def register_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({'error': 'username and password required'}, status=400)

    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({'error': 'username already taken'}, status=400)

    user = CustomUser.objects.create_user(username=username, password=password)
    return JsonResponse({'id': user.id, 'username': user.username}, status=201)


@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({'error': 'username and password required'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'error': 'invalid credentials'}, status=400)

    if not user.is_active:
        return JsonResponse({'error': 'account disabled'}, status=403)

    login(request, user)   # creates session cookie
    return JsonResponse({'message': 'logged in', 'username': user.username})


@csrf_exempt
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'message': 'logged out'})



@login_required
def profile_view(request):
    user = request.user
    return JsonResponse({
        "id": user.id,
        "email": user.email,
        "name": user.get_full_name() or user.username,
    })