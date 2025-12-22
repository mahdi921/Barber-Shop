"""
Serializers for chat API.
"""
from rest_framework import serializers
from .models import FAQ, ChatMessage, ChatSession, LiveChatQueue


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model."""
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'question', 'answer', 'keywords', 'category',
            'is_active', 'priority', 'view_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender_type', 'sender_name', 'content',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_sender_name(self, obj):
        if obj.sender_user:
            return obj.sender_user.phone_number
        return obj.get_sender_type_display()


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    queue_position = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            'id', 'session_key', 'status', 'created_at',
            'last_activity', 'messages', 'queue_position'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']
    
    def get_queue_position(self, obj):
        if hasattr(obj, 'queue_entry'):
            return obj.queue_entry.get_position()
        return None
