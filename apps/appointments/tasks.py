"""
Celery tasks for webhook delivery to Make.com.
"""
import hmac
import hashlib
import json
import random
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import requests

import logging

logger = logging.getLogger(__name__)


def exponential_backoff(retry_count, base_delay=60, max_delay=3600, jitter=True):
    """
    Calculate exponential backoff delay with jitter.
    
    Args:
        retry_count: Number of retries already attempted
        base_delay: Base delay in seconds (default 60s)
        max_delay: Maximum delay in seconds (default 1 hour)
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** retry_count), max_delay)
    
    if jitter:
        delay = delay * (0.5 + random.random())
    
    return int(delay)


def compute_signature(body, secret):
    """
    Compute HMAC-SHA256 signature for webhook payload.
    
    Args:
        body: Request body (bytes or string)
        secret: Secret key for HMAC
    
    Returns:
        Hex digest signature string
    """
    if isinstance(body, str):
        body = body.encode('utf-8')
    
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    
    signature = hmac.new(secret, body, hashlib.sha256).hexdigest()
    return signature


def mask_phone(phone_number):
    """
    Mask phone number for privacy (e.g., 09123456789 -> 0912***6789).
    
    Args:
        phone_number: Iranian phone number string
    
    Returns:
        Masked phone number
    """
    if not phone_number or len(phone_number) < 7:
        return phone_number
    
    # Show first 4 and last 4 digits, mask the middle
    return f"{phone_number[:4]}***{phone_number[-4:]}"


def build_webhook_payload(appointment, event_type):
    """
    Build standardized webhook payload for Make.com.
    
    Args:
        appointment: Appointment instance
        event_type: 'created' or 'confirmed'
    
    Returns:
        Dictionary with webhook payload
    """
    from apps.appointments.models import Appointment
    
    # Ensure we have all related data
    appointment = Appointment.objects.select_related(
        'customer__user',
        'stylist__user',
        'stylist__salon',
        'service'
    ).get(id=appointment.id)
    
    # Build appointment datetime (combine date + time in Tehran timezone)
    from datetime import datetime
    import pytz
    
    tz = pytz.timezone(settings.TIME_ZONE)
    appointment_datetime = datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time
    )
    appointment_datetime = tz.localize(appointment_datetime)
    
    # Calculate end time
    from datetime import timedelta
    duration = timedelta(minutes=appointment.service.duration_minutes)
    end_datetime = appointment_datetime + duration
    
    # Check if this is first-time customer
    from apps.appointments.models import Appointment as AppointmentModel
    is_first_time = AppointmentModel.objects.filter(
        customer=appointment.customer,
        status__in=['confirmed', 'completed']
    ).count() <= 1
    
    payload = {
        'appointment_id': str(appointment.id),
        'event_type': event_type,
        'created_at': appointment.created_at.isoformat(),
        'customer': {
            'id': appointment.customer.id,
            'phone': mask_phone(appointment.customer.user.phone_number),
            'first_name': appointment.customer.first_name,
            'last_name': appointment.customer.last_name,
        },
        'salon': {
            'id': appointment.stylist.salon.id,
            'name': appointment.stylist.salon.name,
            'address': appointment.stylist.salon.address,
        },
        'stylist': {
            'id': appointment.stylist.id,
            'name': appointment.stylist.full_name,
        },
        'services': [{
            'id': appointment.service.id,
            'name': appointment.service.custom_name or appointment.service.get_service_type_display(),
            'price': str(appointment.service.price),
            'duration_minutes': appointment.service.duration_minutes,
        }],
        'total_price': str(appointment.service.price),
        'total_duration_minutes': appointment.service.duration_minutes,
        'appointment_start': appointment_datetime.isoformat(),
        'appointment_end': end_datetime.isoformat(),
        'status': appointment.status,
        'metadata': {
            'is_first_time_customer': is_first_time,
            'source': 'web',
            'persian_date': appointment.jalali_date,
        }
    }
    
    return payload


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def deliver_appointment_webhook(self, appointment_id, event_type):
    """
    Deliver appointment webhook to Make.com with retry logic.
    
    Args:
        appointment_id: UUID or ID of appointment
        event_type: 'created' or 'confirmed'
    
    This task:
    - Builds the webhook payload
    - Computes HMAC signature
    - POSTs to Make.com webhook URL
    - Handles retries with exponential backoff
    - Updates WebhookDelivery and Appointment models
    """
    from apps.appointments.models import Appointment, WebhookDelivery
    
    try:
        appointment = Appointment.objects.select_related(
            'customer__user', 'stylist__salon', 'service'
        ).get(id=appointment_id)
    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} not found for webhook delivery")
        return
    
    # Build payload
    payload = build_webhook_payload(appointment, event_type)
    body = json.dumps(payload, ensure_ascii=False, default=str)
    
    # Get webhook URL from settings
    webhook_url = getattr(settings, 'MAKE_WEBHOOK_URL', '')
    
    # If no URL configured, store as pending
    if not webhook_url:
        idempotency_key = f"appointment:{appointment_id}:{event_type}"
        
        with transaction.atomic():
            delivery, created = WebhookDelivery.objects.get_or_create(
                idempotency_key=idempotency_key,
                defaults={
                    'appointment': appointment,
                    'event_type': event_type,
                    'payload': payload,
                    'status': 'pending',
                    'error_message': 'No webhook URL configured (MAKE_WEBHOOK_URL)',
                }
            )
        
        logger.warning(f"Webhook URL not configured for appointment {appointment_id}")
        return
    
    # Generate signature
    secret = getattr(settings, 'MAKE_WEBHOOK_SECRET', '')
    signature = compute_signature(body, secret)
    
    # Prepare headers
    signature_header = getattr(settings, 'MAKE_SIGNATURE_HEADER', 'X-Make-Signature')
    idempotency_key = f"appointment:{appointment_id}:{event_type}"
    
    headers = {
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotency_key,
        signature_header: f'sha256={signature}',
    }
    
    # Get or create delivery record
    with transaction.atomic():
        delivery, created = WebhookDelivery.objects.select_for_update().get_or_create(
            idempotency_key=idempotency_key,
            defaults={
                'appointment': appointment,
                'event_type': event_type,
                'payload': payload,
                'status': 'sending',
            }
        )
        
        # If not newly created, update status to sending
        if not created and delivery.status != 'sent':
            delivery.status = 'sending'
            delivery.save(update_fields=['status'])
    
    # Make HTTP request
    timeout = getattr(settings, 'MAKE_WEBHOOK_TIMEOUT', 10)
    
    try:
        logger.info(f"Sending webhook for appointment {appointment_id}, event={event_type}, attempt={self.request.retries + 1}")
        
        response = requests.post(
            webhook_url,
            data=body.encode('utf-8'),
            headers=headers,
            timeout=timeout
        )
        
        # Update delivery record
        with transaction.atomic():
            delivery = WebhookDelivery.objects.select_for_update().get(id=delivery.id)
            delivery.attempts_count += 1
            delivery.last_attempt_at = timezone.now()
            delivery.response_code = response.status_code
            delivery.response_body = response.text[:4000]  # Limit to 4000 chars
            
            # Check response status
            if 200 <= response.status_code < 300:
                # Success!
                delivery.status = 'sent'
                delivery.save()
                
                # Update appointment webhook status
                if event_type == 'created':
                    appointment.webhook_created_sent = True
                    appointment.save(update_fields=['webhook_created_sent'])
                elif event_type == 'confirmed':
                    appointment.webhook_confirmed_sent = True
                    appointment.save(update_fields=['webhook_confirmed_sent'])
                
                logger.info(f"Webhook delivered successfully for appointment {appointment_id}, event={event_type}")
                return
            
            elif 500 <= response.status_code < 600:
                # Transient error - retry
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                delivery.save()
                
                # Calculate backoff and retry
                retry_delay = exponential_backoff(self.request.retries)
                logger.warning(
                    f"Webhook delivery failed with {response.status_code} for appointment {appointment_id}, "
                    f"retrying in {retry_delay}s (attempt {self.request.retries + 1}/{self.max_retries})"
                )
                raise self.retry(
                    exc=Exception(f'HTTP {response.status_code}'),
                    countdown=retry_delay
                )
            
            else:
                # 4xx - Permanent failure, don't retry
                delivery.status = 'failed'
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                delivery.save()
                
                logger.error(
                    f"Webhook delivery permanently failed with {response.status_code} "
                    f"for appointment {appointment_id}, event={event_type}"
                )
                return
    
    except requests.RequestException as exc:
        # Network error - retry
        with transaction.atomic():
            delivery = WebhookDelivery.objects.select_for_update().get(id=delivery.id)
            delivery.attempts_count += 1
            delivery.last_attempt_at = timezone.now()
            delivery.error_message = f"Request exception: {str(exc)}"
            delivery.save()
        
        retry_delay = exponential_backoff(self.request.retries)
        logger.warning(
            f"Webhook delivery failed with network error for appointment {appointment_id}, "
            f"retrying in {retry_delay}s: {exc}"
        )
        raise self.retry(exc=exc, countdown=retry_delay)
    
    except Exception as exc:
        # Unexpected error - mark as failed after retries
        if self.request.retries >= self.max_retries:
            with transaction.atomic():
                delivery = WebhookDelivery.objects.select_for_update().get(id=delivery.id)
                delivery.attempts_count += 1
                delivery.last_attempt_at = timezone.now()
                delivery.status = 'failed'
                delivery.error_message = f"Max retries exceeded: {str(exc)}"
                delivery.save()
            
            logger.error(
                f"Webhook delivery failed after {self.max_retries} retries "
                f"for appointment {appointment_id}, event={event_type}: {exc}"
            )
        else:
            retry_delay = exponential_backoff(self.request.retries)
            raise self.retry(exc=exc, countdown=retry_delay)
