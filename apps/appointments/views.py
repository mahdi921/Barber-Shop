"""
Views for appointment booking and management.
"""
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, time

from .models import Appointment
from .serializers import AppointmentSerializer, BookAppointmentSerializer
from .utils import jalali_to_gregorian, generate_time_slots
from apps.accounts.permissions import IsCustomer, IsSalonManager, IsStylist
from apps.accounts.models import StylistProfile
from apps.salons.models import WorkingHours


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomer])
def get_availability(request):
    """
    Get available time slots for a stylist on a specific date.
    
    GET /appointments/api/availability/?stylist_id=1&jalali_date=1402/09/20
    
    Returns list of available time slots.
    """
    stylist_id = request.GET.get('stylist_id')
    jalali_date = request.GET.get('jalali_date')
    
    if not stylist_id or not jalali_date:
        return Response({
            'error': 'stylist_id و jalali_date الزامی هستند'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        stylist = StylistProfile.objects.get(id=stylist_id)
    except StylistProfile.DoesNotExist:
        return Response({'error': 'آرایشگر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    
    # Convert Jalali to Gregorian
    try:
        gregorian_date = jalali_to_gregorian(jalali_date)
    except:
        return Response({'error': 'فرمت تاریخ نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get day of week (0=Saturday, 6=Friday in Persian calendar)
    # Python's weekday: 0=Monday, convert to Persian
    python_weekday = gregorian_date.weekday()
    persian_weekday = (python_weekday + 2) % 7  # Convert to Persian week start (Saturday=0)
    
    # Get working hours for this stylist on this day
    working_hours = WorkingHours.objects.filter(
        Q(stylist=stylist) | Q(salon=stylist.salon),
        day_of_week=persian_weekday,
        is_active=True
    ).first()
    
    if not working_hours:
        return Response({
            'available_slots': [],
            'message': 'در این روز ساعت کاری تعریف نشده است'
        })
    
    # Generate all possible time slots
    all_slots = generate_time_slots(
        working_hours.start_time,
        working_hours.end_time,
        slot_duration_minutes=30
    )
    
    # Get already booked slots
    booked_appointments = Appointment.objects.filter(
        stylist=stylist,
        appointment_date=gregorian_date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_time', flat=True)
    
    # Filter out booked slots
    available_slots = [
        slot.strftime('%H:%M') for slot in all_slots
        if slot not in booked_appointments
    ]
    
    return Response({
        'stylist_id': stylist_id,
        'stylist_name': stylist.full_name,
        'jalali_date': jalali_date,
        'gregorian_date': gregorian_date.isoformat(),
        'available_slots': available_slots,
        'working_hours': {
            'start': working_hours.start_time.strftime('%H:%M'),
            'end': working_hours.end_time.strftime('%H:%M')
        }
    })


from apps.chat.services.notifications import (
    send_appointment_created_notification,
    send_appointment_confirmed_notification,
    send_appointment_cancelled_notification
)

# ... (rest of imports)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def book_appointment(request):
    """
    Book an appointment.
    
    POST /appointments/api/book/
    Body: {
        stylist_id, service_id, jalali_date, time_slot, customer_notes
    }
    """
    serializer = BookAppointmentSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            appointment = serializer.save()
            
            # Auto-Approve Logic
            salon = appointment.stylist.salon
            if salon.auto_approve_appointments:
                appointment.status = 'confirmed'
                appointment.save(update_fields=['status'])
                # Send confirmed notification directly (since signal might only handle pending)
                # But actually signal handles 'created' which is effectively pending.
                # If we save as confirmed immediately, created signal might trigger 'pending' logic if not careful.
                # Let's rely on explicit notification calls here or update signals.
                # To be safe and explicit:
                send_appointment_confirmed_notification(appointment)
            else:
                send_appointment_created_notification(appointment)

            response_serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'نوبت با موفقیت ثبت شد',
                'appointment': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'خطا در ثبت نوبت',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    """
    Get current user's appointments.
    """
    user = request.user
    
    if user.user_type == 'customer':
        appointments = Appointment.objects.filter(
            customer=user.customer_profile
        ).order_by('-appointment_date', '-appointment_time')
    elif user.user_type == 'stylist':
        appointments = Appointment.objects.filter(
            stylist=user.stylist_profile
        ).order_by('-appointment_date', '-appointment_time')
    elif user.user_type == 'salon_manager':
        # Return empty for generic call, use dedicated salon list endpoint
        return Response([]) 
    else:
        return Response({'error': 'نوع کاربر معتبر نیست'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response({
        'count': appointments.count(),
        'appointments': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSalonManager])
def get_salon_appointments(request, salon_id):
    """
    Get appointments for a specific salon (Manager only).
    
    GET /appointments/api/manage/list/<salon_id>/
    """
    try:
        # Verify manager owns the salon
        salon = request.user.manager_profile.salons.get(id=salon_id)
        
        appointments = Appointment.objects.filter(
            stylist__salon=salon
        ).order_by('-appointment_date', '-appointment_time')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            'count': appointments.count(),
            'appointments': serializer.data
        })
    except Exception as e:
        return Response({'error': 'Saloon not found or access denied'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSalonManager])
def approve_appointment(request, appointment_id):
    """
    Approve an appointment.
    
    POST /appointments/api/approve/<id>/
    """
    try:
        appointment = Appointment.objects.select_related('stylist__salon__manager__user').get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'نوبت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        
    # Check permission
    if appointment.stylist.salon.manager.user != request.user:
        return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
        
    if appointment.status != 'pending':
        return Response({'error': 'فقط نوبت‌های در انتظار را می‌توان تأیید کرد'}, status=status.HTTP_400_BAD_REQUEST)
        
    appointment.status = 'confirmed'
    appointment.save(update_fields=['status'])
    
    send_appointment_confirmed_notification(appointment)
    
    return Response({'message': 'نوبت تایید شد'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment.
    
    POST /appointments/api/cancel/<id>/
    Body: { "reason": "some reason" } (Mandatory for managers)
    """
    try:
        appointment = Appointment.objects.select_related('stylist__salon__manager__user').get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'نوبت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    is_customer = user.user_type == 'customer' and appointment.customer.user == user
    is_manager = user.user_type == 'salon_manager' and appointment.stylist.salon.manager.user == user
    
    if not (is_customer or is_manager):
        return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
    
    reason = request.data.get('reason', '')
    
    if is_manager and not reason.strip():
        return Response({'error': 'دلیل لغو الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
    
    from django.utils import timezone
    appointment.status = 'cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.cancelled_by = user
    appointment.cancellation_reason = reason
    appointment.save()
    
    # Notify customer if manager cancelled
    if is_manager:
        send_appointment_cancelled_notification(appointment, reason)
    
    return Response({
        'message': 'نوبت لغو شد',
        'appointment_id': appointment.id
    })
