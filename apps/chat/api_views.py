"""
API views for chat functionality.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import FAQ, ChatSession, ChatMessage, LiveChatQueue
from .serializers import FAQSerializer, ChatSessionSerializer, ChatMessageSerializer
from apps.accounts.permissions import IsSiteAdmin


class FAQViewSet(viewsets.ModelViewSet):
    """
    API endpoint  for FAQ management.
    Admin-only for CUD, public for Read.
    """
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsSiteAdmin()]
    
    def get_queryset(self):
        queryset = FAQ.objects.all()
        
        # Filter active FAQs for non-admin users
        if not (self.request.user and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        
        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-priority', '-created_at')


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def get_active_chats(request):
    """Get list of active chat sessions for admin."""
    sessions = ChatSession.objects.filter(
        status__in=['admin', 'queued']
    ).order_by('-last_activity')
    
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def get_queue(request):
    """Get current chat queue."""
    queue_entries = LiveChatQueue.objects.select_related('session').all()
    
    data = []
    for entry in queue_entries:
        data.append({
            'session_key': entry.session.session_key,
            'reason': entry.reason,
            'priority': entry.priority,
            'position': entry.get_position(),
            'joined_at': entry.joined_at,
            'waiting_time': (entry.joined_at - entry.session.created_at).total_seconds()
        })
    
    return Response(data)


@api_view(['GET'])
def get_chat_history(request, session_key):
    """Get chat history for a session."""
    session = get_object_or_404(ChatSession, session_key=session_key)
    
    # Check permissions
    if not (request.user.is_staff or session.session_key == request.session.session_key):
        return Response(
            {'error': 'دسترسی غیرمجاز'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    messages = session.messages.all()
    serializer = ChatMessageSerializer(messages, many=True)
    
    return Response({
        'session': ChatSessionSerializer(session).data,
        'messages': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsSiteAdmin])
def close_chat_session(request, session_key):
    """Admin closes a chat session."""
    session = get_object_or_404(ChatSession, session_key=session_key)
    
    session.status = 'closed'
    session.save()
    
    # Close any active assignments
    for assignment in session.admin_assignments.filter(is_active=True):
        assignment.leave_chat()
    
    # Remove from queue
    LiveChatQueue.objects.filter(session=session).delete()
    
    return Response({'status': 'closed'})
