"""
Celery tasks for appointments.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

# Tasks for Make.com webhook delivery have been removed in favor of direct Telegram notifications.
