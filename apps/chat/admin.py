from django.contrib import admin
from .models import ChatSession, ChatMessage, FAQ, LiveChatQueue, AdminChatAssignment, AIResponseLog


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'category', 'is_active', 'priority', 'view_count', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    list_editable = ['is_active', 'priority']
    ordering = ['-priority', '-created_at']
    
    def question_preview(self, obj):
        return obj.question[:100] + "..." if len(obj.question) > 100 else obj.question
    question_preview.short_description = 'Question'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key_preview', 'user', 'status', 'assigned_admin', 'last_activity']
    list_filter = ['status', 'created_at']
    search_fields = ['session_key', 'user__phone_number']
    readonly_fields = ['created_at', 'last_activity']
    
    def session_key_preview(self, obj):
        return obj.session_key[:20] + "..."
    session_key_preview.short_description = 'Session'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'sender_type', 'content_preview', 'created_at']
    list_filter = ['sender_type', 'created_at']
    search_fields = ['content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(LiveChatQueue)
class LiveChatQueueAdmin(admin.ModelAdmin):
    list_display = ['session', 'priority', 'joined_at', 'notified_admins']
    list_filter = ['priority', 'notified_admins']
    readonly_fields = ['joined_at']


@admin.register(AdminChatAssignment)
class AdminChatAssignmentAdmin(admin.ModelAdmin):
    list_display = ['admin', 'session', 'is_active', 'joined_at', 'left_at']
    list_filter = ['is_active', 'joined_at']
    readonly_fields = ['joined_at', 'left_at']


@admin.register(AIResponseLog)
class AIResponseLogAdmin(admin.ModelAdmin):
    list_display = ['model', 'tokens_used', 'processing_time_ms', 'created_at']
    list_filter = ['model', 'created_at']
    readonly_fields = ['created_at']
