from django.urls import path
from . import views

urlpatterns = [
    path('compose/', views.compose_view, name='compose'),
    path('contacts/lookup/', views.contacts_lookup, name='contacts_lookup'),
    path('gmail/save-draft/', views.save_draft_view, name='save_draft'),
]
