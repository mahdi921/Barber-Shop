"""
Signal handlers for rating/review cache invalidation.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating, Review
from apps.core.utils import invalidate_salon_cache, invalidate_stylist_cache


@receiver(post_save, sender=Rating)
@receiver(post_delete, sender=Rating)
def invalidate_rating_caches(sender, instance, **kwargs):
    """
    Invalidate salon and stylist rating caches when rating changes.
    Also update salon's cached rating.
    """
    # Invalidate stylist cache
    invalidate_stylist_cache(instance.stylist.id)
    
    # Invalidate and update salon cache
    salon = instance.stylist.salon
    invalidate_salon_cache(salon.id)
    
    # Update salon's cached rating (average of all stylist ratings)
    salon.update_rating_cache()


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def invalidate_review_caches(sender, instance, **kwargs):
    """Invalidate caches when reviews change."""
    invalidate_stylist_cache(instance.stylist.id)
    invalidate_salon_cache(instance.stylist.salon.id)
