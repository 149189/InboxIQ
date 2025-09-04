from django.contrib import admin
from .models import Conversation, Draft

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id','user','created_at','updated_at')
    search_fields = ('user__username',)

@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ('id','user','subject','created_at')
    search_fields = ('subject','user__username')
