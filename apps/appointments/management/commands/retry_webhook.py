"""
Django management command to retry a failed webhook delivery.

Usage:
    python manage.py retry_webhook <delivery_id>
"""
from django.core.management.base import BaseCommand, CommandError
from apps.appointments.models import WebhookDelivery
from apps.appointments.tasks import deliver_appointment_webhook


class Command(BaseCommand):
    help = 'Retry a failed webhook delivery by ID'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'delivery_id',
            type=int,
            help='ID of the WebhookDelivery to retry'
        )
    
    def handle(self, *args, **options):
        delivery_id = options['delivery_id']
        
        try:
            delivery = WebhookDelivery.objects.select_related('appointment').get(id=delivery_id)
        except WebhookDelivery.DoesNotExist:
            raise CommandError(f'WebhookDelivery with ID {delivery_id} does not exist')
        
        # Check if already sent
        if delivery.status == 'sent':
            self.stdout.write(
                self.style.WARNING(
                    f'Webhook {delivery_id} has already been successfully sent. '
                    f'Use resend_appointment_webhook to send a fresh webhook.'
                )
            )
            return
        
        # Reset status and retry
        delivery.status = 'queued'
        delivery.save(update_fields=['status'])
        
        # Queue the task
        deliver_appointment_webhook.delay(
            str(delivery.appointment.id),
            delivery.event_type
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully queued webhook delivery {delivery_id} for retry.\n'
                f'Appointment: {delivery.appointment}\n'
                f'Event Type: {delivery.event_type}\n'
                f'Previous attempts: {delivery.attempts_count}'
            )
        )
