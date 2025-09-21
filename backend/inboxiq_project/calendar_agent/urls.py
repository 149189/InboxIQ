# backend/inboxiq_project/calendar_agent/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Calendar session management
    path('start/', views.start_calendar_session, name='start_calendar_session'),
    path('send/', views.send_calendar_message, name='send_calendar_message'),
    path('history/<str:session_id>/', views.get_calendar_history, name='get_calendar_history'),
]
