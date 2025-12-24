"""
Config API URLs
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.api_config, name='api_config'),
]
