"""
Main chatbot orchestration service.
"""
import logging
from django.utils import timezone
from ..models import ChatSession, ChatMessage, LiveChatQueue
from .faq_matcher import FAQMatcher
from .ai_service import AIService
from .escalation_detector import EscalationDetector

logger = logging.getLogger(__name__)


class ChatbotService:
    """
    Main service that orchestrates chat flow:
    1. FAQ matching
    2. AI fallback
    3. Escalation to admin
    """
    
    def __init__(self, session_key):
        self.session_key = session_key
        self.session = self._get_or_create_session()
        self.faq_matcher = FAQMatcher()
        self.ai_service = AIService()
        self.escalation_detector = EscalationDetector()
    
    def process_message(self, user_message):
        """
        Process user message and return appropriate response.
        Returns dict with response data.
        """
        # Check if session is in admin mode
        if self.session.status == 'admin':
            return self._handle_admin_mode()
        
        # Check if in queue
        if self.session.status == 'queued':
            return self._handle_queue_status()
        
        # 1. Try FAQ first
        faq_result = self._try_faq(user_message)
        if faq_result:
            return faq_result
        
        # 2. Check for escalation keywords
        should_escalate, reason = self.escalation_detector.should_escalate(user_message)
        if should_escalate:
            return self._escalate_to_admin(reason)
        
        # 3. Try AI fallback
        ai_result = self._try_ai(user_message)
        if ai_result:
            # Check if AI suggests escalation
            if ai_result.get('should_escalate'):
                return self._escalate_to_admin('پاسخ هوشمند نامطمئن')
            return ai_result
        
        # 4. Fallback - escalate if nothing worked
        return self._escalate_to_admin('عدم یافتن پاسخ مناسب')
    
    def _try_faq(self, message):
        """Try to match FAQ."""
        faq, confidence = self.faq_matcher.find_match(message)
        
        if faq:
            # Log FAQ hit
            self.faq_matcher.increment_view_count(faq)
            
            # Save bot response
            self._save_bot_message(faq.answer, 'faq')
            
            return {
                'type': 'bot',
                'message': faq.answer,
                'source': 'faq',
                'confidence': confidence,
                'timestamp': timezone.now().isoformat()
            }
        
        return None
    
    def _try_ai(self, message):
        """Try AI-powered response."""
        ai_result = self.ai_service.get_response(message, self.session)
        
        if ai_result:
            # Save bot message
            bot_message = self._save_bot_message(ai_result['content'], 'ai')
            
            # Log AI response
            self.ai_service.log_response(bot_message, ai_result)
            
            return {
                'type': 'bot',
                'message': ai_result['content'],
                'source': 'ai',
                'confidence': ai_result.get('confidence', 0.5),
                'should_escalate': ai_result.get('should_escalate', False),
                'timestamp': timezone.now().isoformat()
            }
        
        return None
    
    def _escalate_to_admin(self, reason):
        """Escalate conversation to admin queue."""
        # Update session status
        self.session.status = 'queued'
        self.session.save()
        
        # Add to queue
        queue_entry, created = LiveChatQueue.objects.get_or_create(
            session=self.session,
            defaults={'reason': reason}
        )
        
        position = queue_entry.get_position()
        
        # Save system message
        self._save_system_message(
            f'درخواست شما به پشتیبانی ارسال شد. موقعیت در صف: {position}'
        )
        
        # Notify admins (via channel layer would be here)
        # TODO: Send WebSocket notification to admins
        
        return {
            'type': 'system',
            'message': f'درخواست شما به پشتیبانی انتقال یافت.\n\nموقعیت در صف: {position}\n\nلطفاً منتظر بمانید تا یکی از کارشناسان به شما پاسخ دهد.',
            'status': 'queued',
            'queue_position': position,
            'timestamp': timezone.now().isoformat()
        }
    
    def _handle_admin_mode(self):
        """Handle message when admin is chatting."""
        admin = self.session.assigned_admin
        admin_name = admin.phone_number if admin else 'پشتیبانی'
        
        return {
            'type': 'system',
            'message': f'شما در حال گفتگو با {admin_name} هستید.\n\nپیام شما دریافت و ارسال شد.',
            'status': 'admin',
            'timestamp': timezone.now().isoformat()
        }
    
    def _handle_queue_status(self):
        """Return current queue status."""
        try:
            queue_entry = self.session.queue_entry
            position = queue_entry.get_position()
            
            return {
                'type': 'system',
                'message': f'شما در صف انتظار هستید.\n\nموقعیت: {position}\n\nلطفاً منتظر بمانید.',
                'status': 'queued',
                'queue_position': position,
                'timestamp': timezone.now().isoformat()
            }
        except:
            return {
                'type': 'system',
                'message': 'در حال بررسی وضعیت...',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_or_create_session(self):
        """Get or create chat session."""
        session, created = ChatSession.objects.get_or_create(
            session_key=self.session_key
        )
        return session
    
    def _save_bot_message(self, content, source='bot'):
        """Save bot message to database."""
        return ChatMessage.objects.create(
            session=self.session,
            sender_type=source if source in ['ai', 'bot'] else 'bot',
            content=content
        )
    
    def _save_system_message(self, content):
        """Save system message."""
        return ChatMessage.objects.create(
            session=self.session,
            sender_type='system',
            content=content
        )
