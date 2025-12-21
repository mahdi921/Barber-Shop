"""
Django management command to resend webhook for an existing appointment.

Usage:
    python manage.py resend_appointment_webhook <appointment_id> [--event-type created|confirmed]
"""
from django.core.management.base import BaseCommand, CommandError
from apps.appointments.models import Appointment
from apps.appointments.tasks import deliver_appointment_webhook


class Command(BaseCommand):
    help = 'Resend webhook for an existing appointment (creates new delivery record)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'appointment_id',
            type=str,
            help='ID of the Appointment to resend webhook for'
        )
        parser.add_argument(
            '--event-type',
            type=str,
            choices=['created', 'confirmed'],
            default='created',
            help='Event type for webhook (default: created)'
        )
    
    def handle(self, *args, **options):
        appointment_id = options['appointment_id']
        event_type = options['event_type']
        
        try:
            appointment = Appointment.objects.select_related(
                'customer', 'stylist', 'service'
            ).get(id=appointment_id)
        except Appointment.DoesNotExist:
            raise CommandError(f'Appointment with ID {appointment_id} does not exist')
        
        # Queue the webhook task
        deliver_appointment_webhook.delay(str(appointment.id), event_type)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully queued webhook for appointment {appointment_id}.\n'
                f'Appointment: {appointment}\n'
                f'Event Type: {event_type}\n'
                f'Customer: {appointment.customer.full_name}\n'
                f'Stylist: {appointment.stylist.full_name}\n'
                f'Date: {appointment.jalali_date} {appointment.appointment_time}'
            )
        )
