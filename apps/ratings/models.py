"""
Rating and Review models with anonymous display.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel
from apps.accounts.models import CustomerProfile, StylistProfile
from apps.salons.models import Salon
from apps.appointments.models import Appointment


class Rating(TimeStampedModel):
    """
    Rating model for stylist services.
    
    Ratings are anonymous when displayed publicly,
    but linked to customer for "my reviews" feature.
    """
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="مشتری"
    )
    
    stylist = models.ForeignKey(
        StylistProfile,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="آرایشگر"
    )
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='rating',
        verbose_name="نوبت"
    )
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز (1-5)"
    )
    
    class Meta:
        verbose_name = "امتیاز"
        verbose_name_plural = "امتیازات"
        ordering = ['-created_at']
        
        # One rating per appointment
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'appointment'],
                name='unique_rating_per_appointment'
            )
        ]
        
        indexes = [
            models.Index(fields=['stylist', 'rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"امتیاز {self.rating} - {self.stylist.full_name}"
    
    @property
    def salon(self):
        """Get salon through stylist."""
        return self.stylist.salon


class Review(TimeStampedModel):
    """
    Text reviews for stylists and salons.
    
    Reviews are displayed anonymously (without customer name).
    """
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="مشتری"
    )
    
    stylist = models.ForeignKey(
        StylistProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="آرایشگر"
    )
    
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name="نوبت"
    )
    
    text = models.TextField(verbose_name="متن نظر")
    
    # Admin moderation
    is_approved = models.BooleanField(default=True, verbose_name="تأیید شده")
    
    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        ordering = ['-created_at']
        
        # One review per appointment
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'appointment'],
                name='unique_review_per_appointment'
            )
        ]
        
        indexes = [
            models.Index(fields=['stylist', 'is_approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"نظر برای {self.stylist.full_name}"
    
    @property
    def salon(self):
        """Get salon through stylist."""
        return self.stylist.salon
