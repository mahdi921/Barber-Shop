"""
Rate limiting for chat messages.
"""
from django.core.cache import cache
from django.conf import settings


class RateLimiter:
    """Simple rate limiter using Django cache."""
    
    def __init__(self):
        self.limit = settings.CHAT_RATE_LIMIT  # messages per minute
        self.window = 60  # seconds
    
    def is_allowed(self, session_key):
        """Check if session is within rate limit."""
        cache_key = f'chat_rate_{session_key}'
        count = cache.get(cache_key, 0)
        
        if count >= self.limit:
            return False
        
        # Increment counter
        cache.set(cache_key, count + 1, self.window)
        return True
    
    def reset(self, session_key):
        """Reset rate limit for session."""
        cache_key = f'chat_rate_{session_key}'
        cache.delete(cache_key)
