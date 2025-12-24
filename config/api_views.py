"""
API endpoint to expose app configuration to frontend.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])
def api_config(request):
    """
    Get public configuration for frontend.
    """
    return Response({
        'telegram_bot_username': settings.TELEGRAM_BOT_USERNAME,
        'telegram_bot_enabled': bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_BOT_USERNAME),
    })
