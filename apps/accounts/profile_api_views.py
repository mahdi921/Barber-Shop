"""
Profile update API endpoints for all user types.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import CustomerProfile, StylistProfile, SalonManagerProfile
from apps.accounts.serializers import (
    CustomerProfileSerializer,
    StylistProfileSerializer,
    SalonManagerProfileSerializer
)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_customer_profile(request):
    """
    Get or update customer profile.
    """
    try:
        profile = request.user.customer_profile
    except AttributeError:
        return Response(
            {'error': 'شما مشتری نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = CustomerProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = CustomerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_stylist_profile(request):
    """
    Get or update stylist profile.
    """
    try:
        profile = request.user.stylist_profile
    except AttributeError:
        return Response(
            {'error': 'شما آرایشگر نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = StylistProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = StylistProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_manager_profile(request):
    """
    Get or update manager profile.
    """
    try:
        profile = request.user.manager_profile
    except AttributeError:
        return Response(
            {'error': 'شما مدیر سالن نیستید'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = SalonManagerProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = SalonManagerProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
