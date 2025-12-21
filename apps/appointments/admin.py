"""Admin configuration for appointments app."""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Appointment, WebhookDelivery


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        'customer', 'stylist', 'jalali_date', 'appointment_time', 
        'status', 'webhook_status_display', 'created_at'
    ]
    list_filter = ['status', 'appointment_date', 'created_at', 'webhook_created_sent', 'webhook_confirmed_sent']
    search_fields = ['customer__first_name', 'customer__last_name', 'stylist__first_name']
    readonly_fields = ['jalali_date', 'created_at', 'updated_at', 'webhook_created_sent', 'webhook_confirmed_sent']
    
    fieldsets = (
        ('اطلاعات نوبت', {
            'fields': ('customer', 'stylist', 'service', 'appointment_date', 'jalali_date', 'appointment_time', 'status')
        }),
        ('یادداشت‌ها', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('لغو', {
            'fields': ('cancelled_at', 'cancelled_by')
        }),
        ('وب‌هوک', {
            'fields': ('webhook_created_sent', 'webhook_confirmed_sent'),
            'classes': ('collapse',),
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def webhook_status_display(self, obj):
        """Display webhook delivery status with icons."""
        created_icon = "✅" if obj.webhook_created_sent else "❌"
        confirmed_icon = "✅" if obj.webhook_confirmed_sent else "❌"
        return format_html(
            'ایجاد: {} | تأیید: {}',
            created_icon,
            confirmed_icon
        )
    webhook_status_display.short_description = 'وضعیت وب‌هوک'


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'appointment_link', 'event_type', 'status', 
        'attempts_count', 'response_code', 'last_attempt_at', 'created_at'
    ]
    list_filter = ['status', 'event_type', 'created_at', 'last_attempt_at']
    search_fields = ['appointment__id', 'idempotency_key', 'appointment__customer__first_name']
    readonly_fields = [
        'appointment', 'event_type', 'payload', 'idempotency_key',
        'attempts_count', 'last_attempt_at', 'response_code', 
        'response_body', 'error_message', 'created_at', 'updated_at',
        'formatted_payload'
    ]
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('appointment', 'event_type', 'status', 'idempotency_key')
        }),
        ('محتوا', {
            'fields': ('formatted_payload',),
        }),
        ('تلاش‌های ارسال', {
            'fields': ('attempts_count', 'last_attempt_at', 'response_code', 'response_body', 'error_message')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['retry_failed_webhooks', 'resend_webhooks']
    
    def appointment_link(self, obj):
        """Link to appointment in admin."""
        url = reverse('admin:appointments_appointment_change', args=[obj.appointment.id])
        return format_html('<a href="{}">{}</a>', url, obj.appointment)
    appointment_link.short_description = 'نوبت'
    
    def formatted_payload(self, obj):
        """Display formatted JSON payload."""
        import json
        try:
            formatted = json.dumps(obj.payload, indent=2, ensure_ascii=False)
            return format_html('<pre style="direction: ltr; text-align: left;">{}</pre>', formatted)
        except:
            return obj.payload
    formatted_payload.short_description = 'محتوای ارسالی (فرمت شده)'
    
    def retry_failed_webhooks(self, request, queryset):
        """Admin action to retry failed webhooks."""
        from apps.appointments.tasks import deliver_appointment_webhook
        
        failed = queryset.filter(status='failed')
        count = 0
        
        for delivery in failed:
            # Re-queue the webhook task
            deliver_appointment_webhook.delay(
                str(delivery.appointment.id),
                delivery.event_type
            )
            count += 1
        
        self.message_user(request, f'{count} وب‌هوک برای ارسال مجدد در صف قرار گرفت.')
    retry_failed_webhooks.short_description = 'ارسال مجدد وب‌هوک‌های ناموفق'
    
    def resend_webhooks(self, request, queryset):
        """Admin action to resend selected webhooks."""
        from apps.appointments.tasks import deliver_appointment_webhook
        
        count = 0
        for delivery in queryset:
            # Reset status and re-queue
            delivery.status = 'queued'
            delivery.save(update_fields=['status'])
            
            deliver_appointment_webhook.delay(
                str(delivery.appointment.id),
                delivery.event_type
            )
            count += 1
        
        self.message_user(request, f'{count} وب‌هوک برای ارسال مجدد در صف قرار گرفت.')
    resend_webhooks.short_description = 'ارسال مجدد وب‌هوک‌های انتخاب شده'

