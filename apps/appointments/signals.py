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
    from apps.appointments.tasks import deliver_appointment_webhook
    
    # Event 1: Appointment created (new record with pending status)
    if created and instance.status == 'pending' and not instance.webhook_created_sent:
        def enqueue_created_webhook():
            logger.info(f"Scheduling 'created' webhook for appointment {instance.id}")
            deliver_appointment_webhook.delay(str(instance.id), 'created')
        
        transaction.on_commit(enqueue_created_webhook)
    
    # Event 2: Appointment confirmed (status changed to 'confirmed')
    previous_status = getattr(instance, '_previous_status', None)
    
    if (not created and 
        instance.status == 'confirmed' and 
        previous_status != 'confirmed' and 
        not instance.webhook_confirmed_sent):
        
        def enqueue_confirmed_webhook():
            logger.info(f"Scheduling 'confirmed' webhook for appointment {instance.id}")
            deliver_appointment_webhook.delay(str(instance.id), 'confirmed')
        
        transaction.on_commit(enqueue_confirmed_webhook)
