"""
Django signals for appointment webhook delivery.
"""
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Appointment

import logging

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Appointment)
def track_status_changes(sender, instance, **kwargs):
    """
    Track appointment status changes to detect confirmation events.
    
    This adds a _previous_status attribute to track when status changes
    from 'pending' to 'confirmed'.
    """
    if instance.pk:
        try:
            previous = Appointment.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Appointment.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Appointment)
def schedule_webhook_on_appointment_event(sender, instance, created, **kwargs):
    """
    Schedule webhook delivery after appointment is created or confirmed.
    
    Two webhook events are triggered:
    1. 'created' - When appointment is first created (status='pending')
    2. 'confirmed' - When appointment status changes to 'confirmed'
    
    Uses transaction.on_commit to ensure webhook is only sent after
    successful database commit.
    """
    
    # Event 1: Appointment created (new record with pending status)
    if created and instance.status == 'pending':
        # Send Telegram notification (if user has Telegram linked)
        transaction.on_commit(
            lambda: __import__('apps.chat.services.notifications', fromlist=['send_appointment_created_notification'])
            .send_appointment_created_notification(instance)
        )
    
    # Event 2: Appointment confirmed (status changed to 'confirmed')
    previous_status = getattr(instance, '_previous_status', None)
    
    if (not created and 
        instance.status == 'confirmed' and 
        previous_status != 'confirmed'):
        
        # Send Telegram notification
        transaction.on_commit(
            lambda: __import__('apps.chat.services.notifications', fromlist=['send_appointment_confirmed_notification'])
            .send_appointment_confirmed_notification(instance)
        )
