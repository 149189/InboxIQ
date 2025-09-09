# backend/inboxiq_project/gmail_agent/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Chat endpoints
    path('chat/start/', views.start_chat_session, name='start_chat_session'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/history/<str:session_id>/', views.get_chat_history, name='get_chat_history'),
    path('chat/sessions/', views.get_user_sessions, name='get_user_sessions'),
    
    # Email endpoints
    path('email/confirm/', views.confirm_email, name='confirm_email'),
]