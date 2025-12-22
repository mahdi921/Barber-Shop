"""
API Views for Salon Management (Manager Dashboard).
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Salon, Service, WorkingHours
from apps.accounts.models import StylistProfile
from .management_serializers import (
    SalonManagementSerializer,
    ServiceSerializer,
    WorkingHoursSerializer
)
from apps.accounts.permissions import IsSalonManager

User = get_user_model()


# ============================================================================
# SALON LIST & CRUD
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsSalonManager])
def api_manager_salons(request):
    """
    List all salons for current manager or create a new salon.
    """
    try:
        manager_profile = request.user.manager_profile
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        salons = manager_profile.salons.all()
        serializer = SalonManagementSerializer(salons, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SalonManagementSerializer(data=request.data)
        if serializer.is_valid():
            salon = serializer.save()
            # Associate salon with manager
            manager_profile.salons.add(salon)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsSalonManager])
def api_manager_salon_detail(request, salon_id):
    """
    Get, update, or delete a specific salon.
    """
    try:
        manager_profile = request.user.manager_profile
        salon = get_object_or_404(Salon, id=salon_id, managers=manager_profile)
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = SalonManagementSerializer(salon)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = SalonManagementSerializer(
            salon, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Remove association or delete salon
        manager_profile.salons.remove(salon)
        # If no more managers, delete the salon
        if salon.managers.count() == 0:
            salon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# STYLIST MANAGEMENT
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsSalonManager])
def api_manager_salon_stylists(request, salon_id):
    """
    List all stylists for a salon or create a new stylist.
    """
    try:
        manager_profile = request.user.manager_profile
        salon = get_object_or_404(Salon, id=salon_id, managers=manager_profile)
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        stylists = salon.stylists.all()
        from apps.accounts.serializers import StylistProfileSerializer
        serializer = StylistProfileSerializer(stylists, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Create User and StylistProfile
        phone_number = request.data.get('phone_number')
        full_name = request.data.get('full_name')
        password = request.data.get('password', 'default123')  # Or generate random

        if not phone_number or not full_name:
            return Response(
                {'error': 'شماره تلفن و نام کامل الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists
        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {'error': 'این شماره تلفن قبلاً ثبت شده است'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create_user(
                    phone_number=phone_number,
                    user_type='stylist',
                    is_active=True
                )
                user.set_password(password)
                user.save()

                # Create StylistProfile
                stylist_profile = StylistProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    salon=salon
                )

                from apps.accounts.serializers import StylistProfileSerializer
                serializer = StylistProfileSerializer(stylist_profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'خطا در ایجاد آرایشگر: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsSalonManager])
def api_manager_stylist_detail(request, stylist_id):
    """
    Get, update, or delete a specific stylist.
    """
    try:
        manager_profile = request.user.manager_profile
        stylist = get_object_or_404(StylistProfile, id=stylist_id)
        
        # Verify manager owns this stylist's salon
        if stylist.salon not in manager_profile.salons.all():
            return Response(
                {'error': 'شما دسترسی به این آرایشگر ندارید'},
                status=status.HTTP_403_FORBIDDEN
            )
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        from apps.accounts.serializers import StylistProfileSerializer
        serializer = StylistProfileSerializer(stylist)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        from apps.accounts.serializers import StylistProfileSerializer
        serializer = StylistProfileSerializer(
            stylist, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Deactivate user instead of deleting
        stylist.user.is_active = False
        stylist.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# LEGACY ENDPOINTS (Keep for backward compatibility)
# ============================================================================

@api_view(['GET', 'PATCH'])
@permission_classes([IsSalonManager])
def api_manager_salon(request):
    """
    Get or update manager's first salon details (legacy).
    """
    try:
        salon = request.user.manager_profile.salons.first()
        if not salon:
            return Response(
                {'error': 'سالنی یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = SalonManagementSerializer(salon)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = SalonManagementSerializer(
            salon, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsSalonManager])
def api_manager_services(request):
    """
    List all services or create a new service.
    """
    try:
        salon = request.user.manager_profile.salons.first()
        if not salon:
            return Response({'error': 'سالنی یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except AttributeError:
        return Response({'error': 'شما مدیر سالن نیستید'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        services = salon.services.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(salon=salon)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsSalonManager])
def api_manager_service_detail(request, service_id):
    """
    Get, update, or delete a specific service.
    """
    try:
        salon = request.user.manager_profile.salons.first()
        service = get_object_or_404(Service, id=service_id, salon=salon)
    except AttributeError:
        return Response({'error': 'شما مدیر سالن نیستید'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsSalonManager])
def api_manager_working_hours(request):
    """
    List all working hours or create new working hours.
    """
    try:
        salon = request.user.manager_profile.salons.first()
        if not salon:
            return Response({'error': 'سالنی یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    except AttributeError:
        return Response({'error': 'شما مدیر سالن نیستید'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        working_hours = salon.working_hours.all()
        serializer = WorkingHoursSerializer(working_hours, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = WorkingHoursSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(salon=salon)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsSalonManager])
def api_manager_working_hours_detail(request, hours_id):
    """
    Get, update, or delete specific working hours.
    """
    try:
        salon = request.user.manager_profile.salons.first()
        working_hours = get_object_or_404(WorkingHours, id=hours_id, salon=salon)
    except AttributeError:
        return Response({'error': 'شما مدیر سالن نیستید'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = WorkingHoursSerializer(working_hours)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = WorkingHoursSerializer(working_hours, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        working_hours.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
