"""
URL configuration for chat app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views, admin_api

router = DefaultRouter()
router.register(r'faqs', api_views.FAQViewSet, basename='faq')

app_name = 'chat'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    path('api/admin/active-chats/', api_views.get_active_chats, name='admin_active_chats'),
    path('api/admin/queue/', api_views.get_queue, name='admin_queue'),
    path('api/admin/queue/detailed/', admin_api.get_detailed_queue, name='admin_queue_detailed'),
    path('api/admin/claim/<str:session_key>/', admin_api.claim_chat, name='claim_chat'),
    path('api/admin/release/<str:session_key>/', admin_api.release_chat, name='release_chat'),
    path('api/history/<str:session_key>/', api_views.get_chat_history, name='chat_history'),
    path('api/admin/close/<str:session_key>/', api_views.close_chat_session, name='close_chat'),
]
