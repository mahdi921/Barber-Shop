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
    
    GET /appointments/api/my-appointments/
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
    else:
        return Response({'error': 'نوع کاربر معتبر نیست'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response({
        'count': appointments.count(),
        'appointments': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment.
    
    POST /appointments/api/cancel/<id>/
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        return Response({'error': 'نوبت یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check permissions: customer or salon manager can cancel
    user = request.user
    allowed = False
    
    if user.user_type == 'customer' and appointment.customer.user == user:
        allowed = True
    elif user.user_type == 'salon_manager':
        if appointment.stylist.salon.manager.user == user:
            allowed = True
    
    if not allowed:
        return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
    
    # Cancel appointment
    from django.utils import timezone
    appointment.status = 'cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.cancelled_by = user
    appointment.save()
    
    return Response({
        'message': 'نوبت لغو شد',
        'appointment_id': appointment.id
    })

# ============================================================================
# Template Views
# ============================================================================

@permission_classes([IsAuthenticated])
def booking_view(request):
    """
    Render booking page.
    """
    context = {}
    stylist_id = request.GET.get('stylist_id')
    if stylist_id:
        try:
            stylist = StylistProfile.objects.get(id=stylist_id)
            context['preselected_stylist'] = stylist
            # Also fetch services for this stylist (or shared salon services)
            # Services are linked to Salon, and optionally Stylist.
            # If service.stylist is None, it's for all. If matches stylist, it's for them.
            services = stylist.salon.services.filter(
                Q(stylist=None) | Q(stylist=stylist)
            )
            context['stylist_services'] = services
        except StylistProfile.DoesNotExist:
            pass
            
    return render(request, 'appointments/booking.html', context)

@permission_classes([IsAuthenticated])
def appointment_list_view(request):
    """
    Render user's appointment list.
    """
    user = request.user
    if user.user_type == 'customer':
        try:
            appointments = Appointment.objects.filter(customer=user.customer_profile).order_by('-appointment_date')
        except:
            appointments = []
    elif user.user_type == 'salon_manager':
        try:
            salon = user.manager_profile.salons.first()
            if salon:
                appointments = Appointment.objects.filter(stylist__salon=salon).order_by('-appointment_date')
            else:
                appointments = []
        except:
            appointments = []
    elif user.user_type == 'stylist':
        try:
            appointments = Appointment.objects.filter(stylist=user.stylist_profile).order_by('-appointment_date')
        except:
            appointments = []
    else:
        appointments = []
        
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})
