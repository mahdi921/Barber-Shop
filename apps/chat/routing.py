"""
WebSocket routing for chat application.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<session_key>[\w-]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/admin/chat/$', consumers.AdminChatConsumer.as_asgi()),
]
