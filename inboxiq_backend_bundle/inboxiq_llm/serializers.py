from rest_framework import serializers
from .models import Conversation, Draft

class MessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user','assistant'])
    content = serializers.CharField()

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

class DraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Draft
        fields = '__all__'
