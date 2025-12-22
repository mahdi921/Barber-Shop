"""
OpenAI integration for AI fallback responses.
"""
import logging
from django.conf import settings
from ..models import ChatMessage, AIResponseLog

logger = logging.getLogger(__name__)

# Only import OpenAI if key is configured
if settings.OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except ImportError:
        client = None
        logger.warning("OpenAI package not installed")
else:
    client = None


class AIService:
    """Service for AI-powered responses using OpenAI."""
    
    SYSTEM_PROMPT = """شما یک دستیار هوشمند برای پلتفرم رزرو آرایشگاه و سالن زیبایی هستید.

وظایف شما:
- پاسخ به سوالات عمومی در مورد خدمات آرایشگاه
- راهنمایی کاربران در فرآیند رزرو
- ارائه اطلاعات کلی در مورد سیستم

محدودیت‌ها:
- هرگز قیمت مشخص اعلام نکنید (بگویید "با سالن تماس بگیرید")
- هرگز رزرو را تأیید نکنید
- اگر سوال پیچیده یا حساس بود، به کاربر بگویید با پشتیبانی تماس بگیرد
- پاسخ‌های کوتاه و مفید بدهید (حداکثر 2-3 جمله)

سبک: مؤدب، حرفه‌ای، و کمک‌کننده
"""

    def get_response(self, user_message, session):
        """
        Get AI-generated response for user message.
        Returns dict with 'content', 'confidence', 'should_escalate'
        """
        if not client:
            return None
        
        try:
            # Get conversation history
            history = self._get_conversation_history(session)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    *history,
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=200,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            ai_response = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Detect if escalation needed
            should_escalate = self._should_escalate(ai_response, finish_reason)
            
            # Estimate confidence (simple heuristic)
            confidence = self._estimate_confidence(ai_response, finish_reason)
            
            return {
                'content': ai_response,
                'confidence': confidence,
                'should_escalate': should_escalate,
                'tokens_used': response.usage.total_tokens,
                'model': response.model
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
    
    def log_response(self, message, ai_result):
        """Log AI response for monitoring."""
        if not ai_result:
            return
        
        AIResponseLog.objects.create(
            message=message,
            prompt=self.SYSTEM_PROMPT,
            response=ai_result['content'],
            model=ai_result.get('model', settings.OPENAI_MODEL),
            confidence=ai_result.get('confidence'),
            tokens_used=ai_result.get('tokens_used', 0)
        )
    
    def _get_conversation_history(self, session, max_messages=5):
        """Get recent conversation history for context."""
        messages = ChatMessage.objects.filter(
            session=session
        ).order_by('-created_at')[:max_messages]
        
        history = []
        for msg in reversed(list(messages)):
            role = 'user' if msg.sender_type == 'user' else 'assistant'
            history.append({
                "role": role,
                "content": msg.content
            })
        
        return history
    
    def _should_escalate(self, response, finish_reason):
        """Determine if response should trigger escalation."""
        # Keywords indicating AI is uncertain
        escalation_phrases = [
            'تماس بگیرید', 'پشتیبانی', 'نمی‌دانم', 'مطمئن نیستم',
            'کارشناس', 'مدیر', 'admin'
        ]
        
        # Check if AI suggests human help
        for phrase in escalation_phrases:
            if phrase in response:
                return True
        
        return finish_reason != 'stop'  # Incomplete response
    
    def _estimate_confidence(self, response, finish_reason):
        """Estimate confidence score based on response characteristics."""
        if finish_reason != 'stop':
            return 0.3
        
        # Longer, structured responses = higher confidence
        word_count = len(response.split())
        
        if word_count < 10:
            return 0.5
        elif word_count < 30:
            return 0.7
        else:
            return 0.8
