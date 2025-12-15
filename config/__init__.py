# config/__init__.py
# This makes the config directory a Python package

# Import celery app to ensure it's loaded when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
