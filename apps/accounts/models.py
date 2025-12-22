"""
User and Profile Models for Salon Booking System.

This module defines:
- CustomUser: Phone-based authentication user model
- CustomerProfile: Profile for customers booking appointments
- SalonManagerProfile: Profile for salon owners/managers
- StylistProfile: Profile for hairstylists
- SiteAdminProfile: Profile for site administrators
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import TimeStampedModel
from .validators import validate_iranian_phone
import jdatetime


class CustomUserManager(BaseUserManager):
    """
    Custom user manager for phone-based authentication.
    """
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and return a regular user with phone number."""
        if not phone_number:
            raise ValueError('شماره تلفن الزامی است')  # Persian: Phone number is required
        
        phone_number = validate_iranian_phone(phone_number)
        user = self.model(phone_number=phone_number, username=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'site_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    """
    Custom user model using Iranian phone number as username.
    
    Replaces default Django user model with phone-based authentication.
    """
    USER_TYPE_CHOICES = [
        ('customer', 'مشتری'),  # Customer
        ('salon_manager', 'مدیر سالن'),  # Salon Manager
        ('stylist', 'آرایشگر'),  # Stylist
        ('site_admin', 'مدیر سایت'),  # Site Admin
    ]
    
    # Override username with phone number
    username = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="نام کاربری (شماره تلفن)"
    )
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[validate_iranian_phone],
        verbose_name="شماره تلفن"
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        verbose_name="نوع کاربر"
    )
    
    # Phone verification fields
    is_phone_verified = models.BooleanField(default=False, verbose_name="تأیید شماره تلفن")
    phone_verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    # Remove email requirement
    email = models.EmailField(blank=True, null=True)
    
    # Override required fields
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone_number'
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.phone_number} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        # Sync username with phone number
        if self.phone_number:
            self.username = self.phone_number
        super().save(*args, **kwargs)


class CustomerProfile(TimeStampedModel):
    """
    Profile for customers who book appointments.
    """
    GENDER_CHOICES = [
        ('male', 'مرد'),  # Male
        ('female', 'زن'),  # Female
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name="کاربر"
    )
    
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    
    selfie_photo = models.ImageField(
        upload_to='customer_photos/',
        verbose_name="عکس سلفی"
    )
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name="جنسیت"
    )
    
    date_of_birth = models.DateField(verbose_name="تاریخ تولد (میلادی)")
    
    # Telegram integration
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="شناسه چت تلگرام",
        help_text="Chat ID برای ارسال اعلان‌های تلگرام"
    )
    
    class Meta:
        verbose_name = "پروفایل مشتری"
        verbose_name_plural = "پروفایل‌های مشتری"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.phone_number})"
    
    @property
    def jalali_date_of_birth(self):
        """Convert Gregorian birth date to Jalali (Persian calendar)."""
        if self.date_of_birth:
            jdate = jdatetime.date.fromgregorian(date=self.date_of_birth)
            return jdate.strftime('%Y/%m/%d')
        return None
    
    @property
    def full_name(self):
        """Return full name."""
        return f"{self.first_name} {self.last_name}"


class SalonManagerProfile(TimeStampedModel):
    """
    Profile for salon managers who operate salons.
    
    Manager accounts require approval by site admin before they can operate.
    """
    SALON_GENDER_CHOICES = [
        ('male', 'مردانه'),  # Male
        ('female', 'زنانه'),  # Female
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='manager_profile',
        verbose_name="کاربر"
    )
    
    salon_name = models.CharField(max_length=100, verbose_name="نام سالن")
    salon_photo = models.ImageField(upload_to='salon_photos/', verbose_name="عکس سالن")
    salon_address = models.TextField(verbose_name="آدرس سالن")
    
    salon_gender_type = models.CharField(
        max_length=10,
        choices=SALON_GENDER_CHOICES,
        verbose_name="نوع سالن (جنسیت)"
    )
    
    # Approval workflow
    is_approved = models.BooleanField(default=False, verbose_name="تأیید شده")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ تأیید")
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_managers',
        verbose_name="تأیید کننده"
    )
    
    class Meta:
        verbose_name = "پروفایل مدیر سالن"
        verbose_name_plural = "پروفایل‌های مدیر سالن"
    
    def __str__(self):
        status = "✓" if self.is_approved else "⏳"
        return f"{status} {self.salon_name} ({self.user.phone_number})"


class StylistProfile(TimeStampedModel):
    """
    Profile for hairstylists who provide services.
    
    Stylists can be created as 'temporary' by salon managers.
    Temporary stylists must complete their profile on first login.
    """
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
    ]
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='stylist_profile',
        verbose_name="کاربر"
    )
    
    # Salon relationship (which salon employs this stylist)
    salon = models.ForeignKey(
        'salons.Salon',
        on_delete=models.CASCADE,
        related_name='stylists',
        verbose_name="سالن"
    )
    
    first_name = models.CharField(max_length=50, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=50, blank=True, verbose_name="نام خانوادگی")
    
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name="جنسیت"
    )
    
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    
    # Temporary stylist workflow
    is_temporary = models.BooleanField(
        default=True,
        verbose_name="حساب موقت",
        help_text="باید در اولین ورود پروفایل را تکمیل کند"
    )
    profile_completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ تکمیل پروفایل")
    
    class Meta:
        verbose_name = "پروفایل آرایشگر"
        verbose_name_plural = "پروفایل‌های آرایشگر"
    
    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"آرایشگر - {self.user.phone_number}"
    
    @property
    def full_name(self):
        """Return full name if available."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return "نام تکمیل نشده"
    
    @property
    def jalali_date_of_birth(self):
        """Convert to Jalali date."""
        if self.date_of_birth:
            jdate = jdatetime.date.fromgregorian(date=self.date_of_birth)
            return jdate.strftime('%Y/%m/%d')
        return None


class SiteAdminProfile(TimeStampedModel):
    """
    Profile for site administrators with full system access.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name="کاربر"
    )
    
    full_name = models.CharField(max_length=100, verbose_name="نام کامل")
    notes = models.TextField(blank=True, verbose_name="یادداشت‌ها")
    
    class Meta:
        verbose_name = "پروفایل مدیر سایت"
        verbose_name_plural = "پروفایل‌های مدیر سایت"
    
    def __str__(self):
        return f"مدیر: {self.full_name}"
