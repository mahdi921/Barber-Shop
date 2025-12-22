"""
FAQ matching service with keyword detection.
"""
import re
from difflib import SequenceMatcher
from ..models import FAQ


class FAQMatcher:
    """Matches user messages to FAQ entries."""
    
    # Persian stop words to ignore
    STOP_WORDS = {
        'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'برای', 'است',
        'یک', 'می', 'شود', 'آن', 'خود', 'تا', 'کند', 'بر', 'هم', 'چه'
    }
    
    def find_match(self, user_message):
        """
        Find best matching FAQ for user message.
        Returns (FAQ object, confidence score) or (None, 0)
        """
        # 1. Try exact match first
        exact_match = self._exact_match(user_message)
        if exact_match:
            return exact_match, 1.0
        
        # 2. Try keyword matching
        keyword_match, score = self._keyword_match(user_message)
        if keyword_match and score > 0.6:
            return keyword_match, score
        
        # 3. Try fuzzy matching (similarity)
        fuzzy_match, score = self._fuzzy_match(user_message)
        if fuzzy_match and score > 0.7:
            return fuzzy_match, score
        
        return None, 0
    
    def _exact_match(self, message):
        """Check for exact question match."""
        return FAQ.objects.filter(
            question__iexact=message.strip(),
            is_active=True
        ).first()
    
    def _keyword_match(self, message):
        """Match based on keywords with scoring."""
        keywords = self._extract_keywords(message)
        if not keywords:
            return None, 0
        
        faqs = FAQ.objects.filter(is_active=True).order_by('-priority')
        best_match = None
        best_score = 0
        
        for faq in faqs:
            if not faq.keywords:
                continue
            
            # Calculate match score based on keyword overlap
            faq_keywords = set(faq.keywords)
            common = keywords & faq_keywords
            
            if common:
                score = len(common) / max(len(keywords), len(faq_keywords))
                if score > best_score:
                    best_score = score
                    best_match = faq
        
        return best_match, best_score
    
    def _fuzzy_match(self, message):
        """Find similar questions using fuzzy string matching."""
        faqs = FAQ.objects.filter(is_active=True).order_by('-priority')
        best_match = None
        best_score = 0
        
        clean_message = message.strip().lower()
        
        for faq in faqs:
            clean_question = faq.question.strip().lower()
            similarity = SequenceMatcher(None, clean_message, clean_question).ratio()
            
            if similarity > best_score:
                best_score = similarity
                best_match = faq
        
        return best_match, best_score
    
    def _extract_keywords(self, text):
        """Extract meaningful keywords from text."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter out stop words and short words
        keywords = {
            word.strip() for word in words
            if len(word) > 2 and word not in self.STOP_WORDS
        }
        
        return keywords
    
    def increment_view_count(self, faq):
        """Increment view count for analytics."""
        faq.view_count += 1
        faq.save(update_fields=['view_count'])
