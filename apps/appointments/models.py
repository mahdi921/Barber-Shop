"""
Appointment booking model with double-booking prevention.
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.models import CustomerProfile, StylistProfile
from apps.salons.models import Service
import jdatetime


class Appointment(TimeStampedModel):
    """
    Appointment model for booking services.
    
    Uses unique constraint to prevent double-booking.
    Stores datetime in UTC, displays in Jalali calendar.
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار تأیید'),  # Pending
        ('confirmed', 'تأیید شده'),  # Confirmed
        ('completed', 'انجام شده'),  # Completed
        ('cancelled', 'لغو شده'),  # Cancelled
    ]
    
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="مشتری"
    )
    
    stylist = models.ForeignKey(
        StylistProfile,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name="آرایشگر"
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments',
        verbose_name="خدمت"
    )
    
    # Appointment date and time (stored in UTC)
    appointment_date = models.DateField(verbose_name="تاریخ نوبت")
    appointment_time = models.TimeField(verbose_name="ساعت نوبت")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="وضعیت"
    )
    
    # Notes
    customer_notes = models.TextField(blank=True, verbose_name="یادداشت مشتری")
    admin_notes = models.TextField(blank=True, verbose_name="یادداشت مدیر")
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ لغو")
    cancelled_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments',
        verbose_name="لغو شده توسط"
    )
    
    # Webhook delivery tracking
    webhook_created_sent = models.BooleanField(
        default=False,
        verbose_name="وب‌هوک ایجاد ارسال شده",
        help_text="آیا وب‌هوک برای ایجاد نوبت ارسال شده است"
    )
    webhook_confirmed_sent = models.BooleanField(
        default=False,
        verbose_name="وب‌هوک تأیید ارسال شده",
        help_text="آیا وب‌هوک برای تأیید نوبت ارسال شده است"
    )
    
    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت‌ها"
        ordering = ['-appointment_date', '-appointment_time']
        
        # Prevent double-booking at database level
        constraints = [
            models.UniqueConstraint(
                fields=['stylist', 'appointment_date', 'appointment_time'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_active_appointment_per_stylist_datetime'
            )
        ]
        
        indexes = [
            models.Index(fields=['stylist', 'appointment_date', 'status']),
            models.Index(fields=['customer', 'appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.stylist.full_name} ({self.jalali_date})"
    
    @property
    def jalali_date(self):
        """Convert appointment date to Jalali (Persian) calendar."""
        if self.appointment_date:
            jdate = jdatetime.date.fromgregorian(date=self.appointment_date)
            return jdate.strftime('%Y/%m/%d')
        return None
    
    @property
    def jalali_datetime_display(self):
        """Full Jalali datetime for display."""
        if self.appointment_date and self.appointment_time:
            jdate = jdatetime.date.fromgregorian(date=self.appointment_date)
            return f"{jdate.strftime('%Y/%m/%d')} - {self.appointment_time.strftime('%H:%M')}"
        return None
    
    def can_be_rated(self):
        """Check if appointment can be rated (must be completed)."""
        return self.status == 'completed'


class WebhookDelivery(TimeStampedModel):
    """
    Track webhook delivery attempts to Make.com.
    
    Each appointment can have multiple webhook deliveries (creation, confirmation).
    Each delivery tracks retry attempts, responses, and status.
    """
    STATUS_CHOICES = [
        ('queued', 'در صف'),  # Queued for delivery
        ('sending', 'در حال ارسال'),  # Currently being sent
        ('sent', 'ارسال شده'),  # Successfully delivered
        ('failed', 'ناموفق'),  # Permanently failed
        ('pending', 'معلق'),  # No webhook URL configured
    ]
    
    EVENT_TYPE_CHOICES = [
        ('created', 'ایجاد شده'),  # Appointment created (pending status)
        ('confirmed', 'تأیید شده'),  # Appointment confirmed
    ]
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='webhook_deliveries',
        verbose_name="نوبت"
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name="نوع رویداد",
        help_text="نوع رویداد که این وب‌هوک برای آن ارسال شده"
    )
    
    payload = models.JSONField(verbose_name="محتوای ارسالی")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued',
        verbose_name="وضعیت"
    )
    
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="کلید یکتایی",
        help_text="کلید یکتا برای جلوگیری از ارسال مجدد (appointment:id:event)"
    )
    
    attempts_count = models.IntegerField(
        default=0,
        verbose_name="تعداد تلاش‌ها"
    )
    
    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخرین تلاش"
    )
    
    response_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="کد پاسخ HTTP"
    )
    
    response_body = models.TextField(
        blank=True,
        verbose_name="پاسخ سرور",
        help_text="پاسخ دریافتی از Make.com (حداکثر 4000 کاراکتر)"
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name="پیام خطا"
    )
    
    class Meta:
        verbose_name = "تحویل وب‌هوک"
        verbose_name_plural = "تحویل‌های وب‌هوک"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['appointment', 'event_type']),
        ]
    
    def __str__(self):
        return f"{self.appointment} - {self.get_event_type_display()} ({self.get_status_display()})"

