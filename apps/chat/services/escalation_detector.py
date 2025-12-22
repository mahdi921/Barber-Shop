"""
Escalation detection service.
"""


class EscalationDetector:
    """Detects when to escalate to human admin."""
    
    # Keywords that trigger immediate escalation
    ESCALATION_KEYWORDS = [
        # Complaints
        'شکایت', 'ناراضی', 'مشکل', 'اشتباه', 'غلط',
        # Payment issues
        'پرداخت', 'پول', 'هزینه', 'بازپرداخت', 'استرداد',
        # Cancellation
        'لغو', 'کنسل', 'cancel',
        # Complex requests
        'مدیر', 'پشتیبانی', 'کارشناس', 'مسئول', 'admin',
        #Negative sentiment
        'بد', 'ضعیف', 'افتضاح'
    ]
    
    def should_escalate(self, message, ai_confidence=None):
        """
        Determine if message should be escalated.
        Returns (should_escalate: bool, reason: str)
        """
        message_lower = message.lower()
        
        # 1. Check for escalation keywords
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                return True, f'کلمه کلیدی: {keyword}'
        
        # 2. Check AI confidence if provided
        if ai_confidence is not None and ai_confidence < 0.5:
            return True, 'اطمینان پایین سیستم هوشمند'
        
        # 3. Very long messages might be complex
        if len(message.split()) > 50:
            return True, 'پیام پیچیده و طولانی'
        
        return False, None
