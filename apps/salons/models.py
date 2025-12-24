"""
Models for Salons, Services, and Working Hours.
"""
from django.db import models
from apps.core.models import TimeStampedModel
from apps.accounts.models import SalonManagerProfile
from django.core.validators import MinValueValidator


class SalonQuerySet(models.QuerySet):
    """Custom QuerySet for gender-based filtering."""
    
    def approved(self):
        """Return only approved salons."""
        return self.filter(manager__is_approved=True)
    
    def for_gender(self, gender):
        """
        Filter salons by customer gender.
        Male customers see only male salons, female see only female.
        """
        return self.filter(gender_type=gender, manager__is_approved=True)


class Salon(TimeStampedModel):
    """
    Salon model representing a barbershop or beauty salon.
    
    Gender-based: Male salons serve male customers, female salons serve female customers.
    """
    GENDER_TYPE_CHOICES = [
        ('male', 'مردانه'),  # Male
        ('female', 'زنانه'),  # Female
    ]
    
    manager = models.ForeignKey(
        SalonManagerProfile,
        on_delete=models.CASCADE,
        related_name='salons',
        verbose_name="مدیر سالن"
    )
    
    name = models.CharField(max_length=100, verbose_name="نام سالن")
    photo = models.ImageField(upload_to='salon_photos/', verbose_name="عکس سالن")
    address = models.TextField(verbose_name="آدرس")
    
    gender_type = models.CharField(
        max_length=10,
        choices=GENDER_TYPE_CHOICES,
        verbose_name="نوع سالن",
        help_text="مردانه فقط برای مردان، زنانه فقط برای زنان"
    )
    
    # Cached rating fields (updated when ratings change)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name="میانگین امتیاز"
    )
    total_ratings = models.IntegerField(default=0, verbose_name="تعداد امتیازها")
    
    # Settings
    auto_approve_appointments = models.BooleanField(
        default=False,
        verbose_name="تأیید خودکار نوبت‌ها",
        help_text="در صورت فعال بودن، نوبت‌ها بلافاصله تأیید می‌شوند"
    )
    
    objects = SalonQuerySet.as_manager()
    
    class Meta:
        verbose_name = "سالن"
        verbose_name_plural = "سالن‌ها"
        ordering = ['-average_rating', '-created_at']
        indexes = [
            models.Index(fields=['gender_type', 'average_rating']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_gender_type_display()})"
    
    def update_rating_cache(self):
        """
        Update cached average rating from stylist ratings.
        Salon rating = average of all its stylists' ratings.
        """
        from apps.ratings.models import Rating
        from django.db.models import Avg, Count
        
        # Get all ratings for stylists in this salon
        stylist_ratings = Rating.objects.filter(
            stylist__salon=self
        ).aggregate(
            avg=Avg('rating'),
            count=Count('id')
        )
        
        self.average_rating = stylist_ratings['avg'] or 0
        self.total_ratings = stylist_ratings['count'] or 0
        self.save(update_fields=['average_rating', 'total_ratings'])


class Service(TimeStampedModel):
    """
    Services offered by salons/stylists.
    
    Service types are gender-specific:
    - Male salons: haircut, facial/hair trimming
    - Female salons: haircut, coloring, nails, makeup, eyelashes, lips, piercing, facial
    """
    MALE_SERVICE_TYPES = [
        ('haircut', 'کوتاهی مو'),  # Haircut
        ('shave', 'اصلاح'),  # Shaving
        ('beard_trim', 'اصلاح ریش'),  # Beard trimming
        ('facial', 'مراقبت از پوست'),  # Facial
    ]
    
    FEMALE_SERVICE_TYPES = [
        ('haircut', 'کوتاهی مو'),
        ('hair_color', 'رنگ مو'),  # Hair coloring
        ('nails', 'خدمات ناخن'),  # Nails
        ('makeup', 'آرایش'),  # Makeup
        ('eyelashes', 'خدمات مژه'),  # Eyelashes
        ('lips', 'خدمات لب'),  # Lips
        ('piercing', 'سوراخ کردن'),  # Piercing
        ('facial', 'مراقبت از پوست'),  # Facial
        ('facial_hair', 'اصلاح ابرو و صورت'),  # Eyebrow/facial hair
    ]
    
    ALL_SERVICE_TYPES = list(set(MALE_SERVICE_TYPES + FEMALE_SERVICE_TYPES))
    
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name="سالن"
    )
    
    # Optional: specific stylist offering this service
    stylist = models.ForeignKey(
        'accounts.StylistProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='services',
        verbose_name="آرایشگر",
        help_text="اگر خالی باشد، همه آرایشگرها این سرویس را ارائه می‌دهند"
    )
    
    service_type = models.CharField(
        max_length=50,
        choices=ALL_SERVICE_TYPES,
        verbose_name="نوع خدمت"
    )
    
    custom_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="نام سفارشی",
        help_text="نام خاص برای این خدمت (اختیاری)"
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت (تومان)"
    )
    
    duration_minutes = models.IntegerField(
        default=30,
        verbose_name="مدت زمان (دقیقه)"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"
        ordering = ['salon', 'service_type']
    
    def __str__(self):
        name = self.custom_name if self.custom_name else self.get_service_type_display()
        stylist_info = f" ({self.stylist.full_name})" if self.stylist else ""
        return f"{name} - {self.salon.name}{stylist_info}"
    
    def clean(self):
        """Validate service type matches salon gender."""
        from django.core.exceptions import ValidationError
        
        male_types = [s[0] for s in self.MALE_SERVICE_TYPES]
        female_types = [s[0] for s in self.FEMALE_SERVICE_TYPES]
        
        if self.salon.gender_type == 'male' and self.service_type in female_types and self.service_type not in male_types:
            raise ValidationError("این نوع خدمت برای سالن مردانه مجاز نیست")
        
        # Note: Some services like haircut and facial are valid for both


class WorkingHours(TimeStampedModel):
    """
    Working hours for salons or specific stylists.
    
    Can be defined at salon level (all stylists) or stylist level (individual).
    """
    WEEKDAY_CHOICES = [
        (0, 'شنبه'),  # Saturday
        (1, 'یکشنبه'),  # Sunday
        (2, 'دوشنبه'),  # Monday
        (3, 'سه‌شنبه'),  # Tuesday
        (4, 'چهارشنبه'),  # Wednesday
        (5, 'پنج‌شنبه'),  # Thursday
        (6, 'جمعه'),  # Friday
    ]
    
    # Either salon-level or stylist-level (one must be set)
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='working_hours',
        verbose_name="سالن"
    )
    
    stylist = models.ForeignKey(
        'accounts.StylistProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='working_hours',
        verbose_name="آرایشگر"
    )
    
    day_of_week = models.IntegerField(
        choices=WEEKDAY_CHOICES,
        verbose_name="روز هفته"
    )
    
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")
    
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"
        ordering = ['day_of_week', 'start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(salon__isnull=False) | models.Q(stylist__isnull=False),
                name='workinghours_has_salon_or_stylist'
            )
        ]
    
    def __str__(self):
        entity = self.salon.name if self.salon else self.stylist.full_name
        return f"{entity} - {self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"
    
    def clean(self):
        """Validate that either salon or stylist is set, not both."""
        from django.core.exceptions import ValidationError
        
        if not self.salon and not self.stylist:
            raise ValidationError("باید سالن یا آرایشگر انتخاب شود")
        
        if self.salon and self.stylist:
            raise ValidationError("نمی‌توان هم سالن و هم آرایشگر را انتخاب کرد")
        
        if self.start_time >= self.end_time:
            raise ValidationError("ساعت شروع باید قبل از ساعت پایان باشد")
