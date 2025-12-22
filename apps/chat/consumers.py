"""
WebSocket consumers for chat system.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatSession, ChatMessage, LiveChatQueue
from .services.chatbot import ChatbotService
from .services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer for user chat sessions.
    """
    
    async def connect(self):
        self.session_key = self.scope['url_route']['kwargs']['session_key']
        self.room_group_name = f'chat_{self.session_key}'
        self.rate_limiter = RateLimiter()
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': 'به سیستم چت خوش آمدید! چطور می‌توانم کمکتان کنم؟',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages from user."""
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            
            if not message:
                return
            
            # Rate limiting
            if not await self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'لطفاً کمی صبر کنید. پیام‌های شما خیلی سریع ارسال می‌شوند.',
                    'timestamp': timezone.now().isoformat()
                }))
                return
            
            # Save user message
            await self.save_message(message, 'user')
            
            # Process message and get response
            response = await self.process_message(message)
            
            # Send response
            await self.send(text_data=json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error in chat consumer: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'خطایی رخ داد. لطفاً دوباره تلاش کنید.',
                'timestamp': timezone.now().isoformat()
            }))
    
    async def process_message(self, message):
        """Route message to appropriate handler."""
        @database_sync_to_async
        def _process():
            chatbot = ChatbotService(self.session_key)
            return chatbot.process_message(message)
        
        return await _process()

    
    @database_sync_to_async
    def save_message(self, content, sender_type):
        """Save message to database."""
        session, _ = ChatSession.objects.get_or_create(
            session_key=self.session_key
        )
        ChatMessage.objects.create(
            session=session,
            sender_type=sender_type,
            content=content
        )
    
    @database_sync_to_async
    def check_rate_limit(self):
        """Check if user has exceeded rate limit."""
        return self.rate_limiter.is_allowed(self.session_key)
    
    async def chat_message(self, event):
        """Receive message from room group."""
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'sender': event.get('sender', 'bot'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))


class AdminChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer for admin chat dashboard.
    """
    
    async def connect(self):
        # Verify admin user
        user = self.scope.get('user')
        if not user or not user.is_authenticated or user.user_type != 'site_admin':
            await self.close()
            return
        
        self.admin_id = user.id
        self.admin_group_name = 'admin_chat_notifications'
        
        # Join admin notification group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current queue status
        queue_count = await self.get_queue_count()
        await self.send(text_data=json.dumps({
            'type': 'queue_status',
            'count': queue_count,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        # Leave admin group
        await self.channel_layer.group_discard(
            self.admin_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle admin actions."""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'join_chat':
                session_key = data.get('session_key')
                await self.join_user_chat(session_key)
            
            elif action == 'send_message':
                session_key = data.get('session_key')
                message = data.get('message')
                await self.send_admin_message(session_key, message)
            
            elif action == 'leave_chat':
                session_key = data.get('session_key')
                await self.leave_user_chat(session_key)
                
        except Exception as e:
            logger.error(f"Error in admin consumer: {str(e)}")
    
    @database_sync_to_async
    def get_queue_count(self):
        """Get number of users in queue."""
        return LiveChatQueue.objects.count()
    
    @database_sync_to_async
    def join_user_chat(self, session_key):
        """Admin joins a user's chat."""
        from .models import AdminChatAssignment
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        admin = User.objects.get(id=self.admin_id)
        session = ChatSession.objects.get(session_key=session_key)
        
        # Create assignment
        AdminChatAssignment.objects.create(
            session=session,
            admin=admin
        )
        
        # Update session status
        session.status = 'admin'
        session.assigned_admin = admin
        session.save()
        
        # Remove from queue if exists
        LiveChatQueue.objects.filter(session=session).delete()
        
        return True
    
    @database_sync_to_async
    def send_admin_message(self, session_key, message):
        """Send message from admin to user."""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        admin = User.objects.get(id=self.admin_id)
        session = ChatSession.objects.get(session_key=session_key)
        
        # Save message
        ChatMessage.objects.create(
            session=session,
            sender_type='admin',
            sender_user=admin,
            content=message
        )
        
        return True
    
    @database_sync_to_async
    def leave_user_chat(self, session_key):
        """Admin leaves user chat."""
        session = ChatSession.objects.get(session_key=session_key)
        
        # Mark assignment as inactive
        from .models import AdminChatAssignment
        assignment = AdminChatAssignment.objects.filter(
            session=session,
            admin_id=self.admin_id,
            is_active=True
        ).first()
        
        if assignment:
            assignment.leave_chat()
        
        # Update session status back to bot
        session.status = 'bot'
        session.assigned_admin = None
        session.save()
        
        return True
    
    async def queue_notification(self, event):
        """Notify admin of new queue entry."""
        await self.send(text_data=json.dumps({
            'type': 'queue_update',
            'count': event['count'],
            'session_key': event.get('session_key'),
            'timestamp': timezone.now().isoformat()
        }))
