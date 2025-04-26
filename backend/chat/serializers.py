# chat/serializers.py
from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'created_at']
        read_only_fields = ['created_at']

class ChatSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'is_active', 'message_count', 'last_message']
        read_only_fields = ['created_at', 'user', 'message_count', 'last_message']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:50],
                'sender': last_message.sender,
                'created_at': last_message.created_at
            }
        return None