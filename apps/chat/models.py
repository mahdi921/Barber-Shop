"""
Chat application models for support chatbot system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatSession(models.Model):
    """
    Represents a chat session between a user and the system.
    Can be anonymous (no user) or authenticated.
    """
    STATUS_CHOICES = [
        ('bot', 'Bot Mode'),
        ('queued', 'Waiting in Queue'),
        ('admin', 'Admin Chat'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    session_key = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='bot')

    # Chat locking mechanism - prevents double-join
    locked_by_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_chats',
        help_text='Admin who has locked/claimed this chat'
    )
    locked_at = models.DateTimeField(null=True, blank=True, help_text='When chat was locked')
    
    assigned_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_chat_sessions'
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['status', '-last_activity']),
        ]
    
    def __str__(self):
        return f"Chat {self.session_key} - {self.get_status_display()}"


class ChatMessage(models.Model):
    """
    Individual message in a chat session.
    """
    SENDER_TYPE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('admin', 'Admin'),
        ('ai', 'AI'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPE_CHOICES)
    sender_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # AI confidence, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.content[:50]}"


class FAQ(models.Model):
    """
    Frequently Asked Questions with keyword matching.
    """
    question = models.TextField()
    answer = models.TextField()
    keywords = models.JSONField(default=list, blank=True)  # List of Persian keywords
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher priority FAQs are matched first")
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return f"{self.question[:50]}..."


class LiveChatQueue(models.Model):
    """
    Queue for users waiting for admin assistance.
    """
    session = models.OneToOneField(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='queue_entry'
    )
    reason = models.TextField(blank=True)  # Why escalated
    priority = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    notified_admins = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-priority', 'joined_at']
    
    def __str__(self):
        return f"Queue: {self.session.session_key}"
    
    def get_position(self):
        """Get position in queue (1-indexed)."""
        earlier = LiveChatQueue.objects.filter(
            joined_at__lt=self.joined_at
        ).count()
        return earlier + 1


class AdminChatAssignment(models.Model):
    """
    Tracks admin assignments to chat sessions.
    """
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='admin_assignments'
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_assignments'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.admin.phone_number} → {self.session.session_key}"
    
    def leave_chat(self):
        """Mark assignment as inactive."""
        self.is_active = False
        self.left_at = timezone.now()
        self.save()


class AIResponseLog(models.Model):
    """
    Logs AI-generated responses for monitoring and improvement.
    """
    message = models.OneToOneField(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='ai_log'
    )
    prompt = models.TextField()
    response = models.TextField()
    model = models.CharField(max_length=50)  # e.g., "gpt-4o-mini"
    confidence = models.FloatField(null=True, blank=True)
    tokens_used = models.IntegerField(default=0)
    processing_time_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Log: {self.model} - {self.created_at}"
