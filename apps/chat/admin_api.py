"""
Additional API endpoints for admin chat queue management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import ChatSession, LiveChatQueue, AdminChatAssignment
from .serializers import ChatSessionSerializer
from apps.accounts.permissions import IsSiteAdmin


@api_view(['POST'])
@permission_classes([IsSiteAdmin])
def claim_chat(request, session_key):
    """
    Admin claims/locks a chat from the queue.
    Prevents multiple admins from joining the same chat.
    """
    try:
        with transaction.atomic():
            # Lock the session row to prevent race conditions
            session = ChatSession.objects.select_for_update().get(
                session_key=session_key
            )
            
            # Check if already locked
            if session.locked_by_admin and session.locked_by_admin != request.user:
                return Response({
                    'error': 'این چت توسط ادمین دیگری قفل شده است',
                    'locked_by': session.locked_by_admin.phone_number
                }, status=status.HTTP_409_CONFLICT)
            
            # Claim the chat
            session.locked_by_admin = request.user
            session.locked_at = timezone.now()
            session.status = 'admin'
            session.assigned_admin = request.user
            session.save()
            
            # Create assignment record
            AdminChatAssignment.objects.create(
                session=session,
                admin=request.user
            )
            
            # Remove from queue
            LiveChatQueue.objects.filter(session=session).delete()
            
            return Response({
                'success': True,
                'session': ChatSessionSerializer(session).data,
                'message': 'چت با موفقیت انتخاب شد'
            })
            
    except ChatSession.DoesNotExist:
        return Response({
            'error': 'چت یافت نشد'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsSiteAdmin])
def release_chat(request, session_key):
    """
    Admin releases a locked chat back to queue or closes it.
    """
    try:
        with transaction.atomic():
            session = ChatSession.objects.select_for_update().get(
                session_key=session_key
            )
            
            # Only the admin who locked it can release
            if session.locked_by_admin != request.user:
                return Response({
                    'error': 'شما مجاز به آزاد کردن این چت نیستید'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Release the lock
            session.locked_by_admin = None
            session.locked_at = None
            
            # Check if should close or return to queue
            close_chat = request.data.get('close', False)
            
            if close_chat:
                session.status = 'closed'
                # Mark assignment as complete
                session.admin_assignments.filter(
                    admin=request.user,
                    is_active=True
                ).update(is_active=False, left_at=timezone.now())
            else:
                # Return to queue
                session.status = 'queued'
                LiveChatQueue.objects.get_or_create(
                    session=session,
                    defaults={'reason': 'بازگشت به صف'}
                )
            
            session.save()
            
            return Response({
                'success': True,
                'message': 'چت اب‌رای شد' if not close_chat else 'چت بسته شد'
            })
            
    except ChatSession.DoesNotExist:
        return Response({
            'error': 'چت یافت نشد'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def get_detailed_queue(request):
    """
    Get enhanced queue information with last message preview.
    """
    queue_entries = LiveChatQueue.objects.select_related(
        'session', 'session__user'
    ).prefetch_related('session__messages').all()
    
    data = []
    for entry in queue_entries:
        last_message = entry.session.messages.order_by('-created_at').first()
        
        data.append({
            'session_key': entry.session.session_key,
            'user_name': entry.session.user.customer_profile.full_name if entry.session.user and hasattr(entry.session.user, 'customer_profile') else 'کاربر مهمان',
            'reason': entry.reason,
            'priority': entry.priority,
            'position': entry.get_position(),
            'joined_at': entry.joined_at.isoformat(),
            'waiting_time': (timezone.now() - entry.joined_at).total_seconds(),
            'last_message': last_message.content[:100] if last_message else None,
            'is_locked': entry.session.locked_by_admin is not None,
            'locked_by': entry.session.locked_by_admin.phone_number if entry.session.locked_by_admin else None
        })
    
    return Response(data)
