"""
Django admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import (
    CustomUser, CustomerProfile, SalonManagerProfile,
    StylistProfile, SiteAdminProfile
)


class CustomerProfileInline(admin.StackedInline):
    """Inline admin for customer profile."""
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'پروفایل مشتری'
    fields = ['first_name', 'last_name', 'selfie_photo', 'gender', 'date_of_birth']


class SalonManagerProfileInline(admin.StackedInline):
    """Inline admin for salon manager profile."""
    model = SalonManagerProfile
    can_delete = False
    verbose_name_plural = 'پروفایل مدیر سالن'
    fields = [
        'salon_name', 'salon_photo', 'salon_address', 'salon_gender_type',
        'is_approved', 'approved_at', 'approved_by'
    ]
    readonly_fields = ['approved_at', 'approved_by']


class StylistProfileInline(admin.StackedInline):
    """Inline admin for stylist profile."""
    model = StylistProfile
    can_delete = False
    verbose_name_plural = 'پروفایل آرایشگر'
    fields = [
        'salon', 'first_name', 'last_name', 'gender', 'date_of_birth',
        'is_temporary', 'profile_completed_at'
    ]
    readonly_fields = ['profile_completed_at']


class SiteAdminProfileInline(admin.StackedInline):
    """Inline admin for site admin profile."""
    model = SiteAdminProfile
    can_delete = False
    verbose_name_plural = 'پروفایل مدیر سایت'
    fields = ['full_name', 'notes']


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom user admin with phone-based authentication.
    """
    list_display = ['phone_number', 'user_type', 'is_phone_verified', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_phone_verified', 'date_joined']
    search_fields = ['phone_number', 'username']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('user_type', 'is_phone_verified')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def get_inline_instances(self, request, obj=None):
        """Show appropriate profile inline based on user type."""
        if not obj:
            return []
        
        inlines = []
        if obj.user_type == 'customer':
            inlines.append(CustomerProfileInline(self.model, self.admin_site))
        elif obj.user_type == 'salon_manager':
            inlines.append(SalonManagerProfileInline(self.model, self.admin_site))
        elif obj.user_type == 'stylist':
            inlines.append(StylistProfileInline(self.model, self.admin_site))
        elif obj.user_type == 'site_admin':
            inlines.append(SiteAdminProfileInline(self.model, self.admin_site))
        
        return inlines


@admin.register(SalonManagerProfile)
class SalonManagerProfileAdmin(admin.ModelAdmin):
    """
    Admin for salon manager profiles with approval actions.
    """
    list_display = ['salon_name', 'get_phone', 'salon_gender_type', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'salon_gender_type', 'created_at']
    search_fields = ['salon_name', 'user__phone_number', 'salon_address']
    readonly_fields = ['approved_at', 'approved_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات سالن', {
            'fields': ('user', 'salon_name', 'salon_photo', 'salon_address', 'salon_gender_type')
        }),
        ('تأیید', {
            'fields': ('is_approved', 'approved_at', 'approved_by')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_managers']
    
    def get_phone(self, obj):
        """Get phone number from user."""
        return obj.user.phone_number
    get_phone.short_description = 'شماره تلفن'
    
    def approve_managers(self, request, queryset):
        """Bulk approve salon managers."""
        updated = 0
        for manager in queryset.filter(is_approved=False):
            manager.is_approved = True
            manager.approved_at = timezone.now()
            manager.approved_by = request.user
            manager.save()
            updated += 1
        
        self.message_user(request, f'{updated} مدیر سالن تأیید شد')
    approve_managers.short_description = 'تأیید مدیران انتخاب شده'


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    """Admin for customer profiles."""
    list_display = ['get_full_name', 'get_phone', 'gender', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'user__phone_number']
    readonly_fields = ['created_at', 'updated_at', 'jalali_date_of_birth']
    
    fieldsets = (
        ('کاربر', {'fields': ('user',)}),
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'selfie_photo', 'gender', 'date_of_birth', 'jalali_date_of_birth')
        }),
        ('تاریخ‌ها', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = 'نام کامل'
    
    def get_phone(self, obj):
        return obj.user.phone_number
    get_phone.short_description = 'شماره تلفن'


@admin.register(StylistProfile)
class StylistProfileAdmin(admin.ModelAdmin):
    """Admin for stylist profiles."""
    list_display = ['get_name', 'get_phone', 'salon', 'gender', 'is_temporary']
    list_filter = ['is_temporary', 'gender', 'salon']
    search_fields = ['first_name', 'last_name', 'user__phone_number']
    readonly_fields = ['profile_completed_at', 'created_at', 'updated_at']
    
    def get_name(self, obj):
        return obj.full_name
    get_name.short_description = 'نام'
    
    def get_phone(self, obj):
        return obj.user.phone_number
    get_phone.short_description = 'شماره تلفن'


@admin.register(SiteAdminProfile)
class SiteAdminProfileAdmin(admin.ModelAdmin):
    """Admin for site admin profiles."""
    list_display = ['full_name', 'get_phone', 'created_at']
    search_fields = ['full_name', 'user__phone_number']
    
    def get_phone(self, obj):
        return obj.user.phone_number
    get_phone.short_description = 'شماره تلفن'
