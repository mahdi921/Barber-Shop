"""
Views for user authentication, registration, and profile management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CustomUser, SalonManagerProfile, StylistProfile
from .forms import (
    CustomerRegistrationForm, SalonManagerRegistrationForm,
    LoginForm, StylistProfileCompletionForm
)
from .serializers import (
    CustomerRegistrationSerializer, SalonManagerRegistrationSerializer,
    StylistProfileCompletionSerializer, CustomUserSerializer
)
from .permissions import IsSalonManager, IsStylist, IsSiteAdmin


# ============================================================================
# Template-based Views (MPA)
# ============================================================================

def register_customer_view(request):
    """
    Customer registration page with CAPTCHA.
    """
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.')  # Registration successful
            return redirect('accounts:login')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register_customer.html', {'form': form})


def register_manager_view(request):
    """
    Salon manager registration page with CAPTCHA.
    Requires admin approval before salon can operate.
    """
    if request.method == 'POST':
        form = SalonManagerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.info(
                request,
                'ثبت‌نام شما ثبت شد. پس از تأیید مدیر سایت می‌توانید وارد شوید.'  # Pending admin approval
            )
            return redirect('accounts:login')
    else:
        form = SalonManagerRegistrationForm()
    
    return render(request, 'accounts/register_manager.html', {'form': form})


def login_view(request):
    """
    Phone-based login view with CAPTCHA.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=phone_number, password=password)
            
            if user is not None:
                login(request, user)
                
                # Redirect based on user type
                if user.user_type == 'customer':
                    return redirect('accounts:customer_dashboard')
                elif user.user_type == 'salon_manager':
                    return redirect('accounts:manager_dashboard')
                elif user.user_type == 'stylist':
                    # Check if stylist profile is temporary
                    try:
                        if user.stylist_profile.is_temporary:
                            return redirect('accounts:stylist_complete_profile')
                    except StylistProfile.DoesNotExist:
                        pass
                    return redirect('accounts:stylist_dashboard')
                elif user.user_type == 'site_admin':
                    return redirect('admin:index')
                else:
                    return redirect('accounts:customer_dashboard')
            else:
                messages.error(request, 'شماره تلفن یا رمز عبور اشتباه است')  # Invalid credentials
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید')  # Logged out successfully
    return redirect('accounts:login')


@login_required
def stylist_complete_profile_view(request):
    """
    View for temporary stylists to complete their profile on first login.
    """
    try:
        stylist_profile = request.user.stylist_profile
    except AttributeError:
        messages.error(request, 'پروفایل آرایشگر یافت نشد')
        return redirect('accounts:login')
    
    if not stylist_profile.is_temporary:
        # Already completed
        return redirect('accounts:stylist_dashboard')
    
    if request.method == 'POST':
        form = StylistProfileCompletionForm(request.POST, instance=stylist_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_temporary = False
            profile.profile_completed_at = timezone.now()
            profile.save()
            
            messages.success(request, 'پروفایل شما تکمیل شد')  # Profile completed
            return redirect('accounts:stylist_dashboard')
    else:
        form = StylistProfileCompletionForm(instance=stylist_profile)
    
    return render(request, 'accounts/stylist_complete_profile.html', {'form': form})


@login_required
def customer_dashboard(request):
    """Customer dashboard showing salons and appointments."""
    if request.user.user_type != 'customer':
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('accounts:login')
    
    customer_profile = request.user.customer_profile
    
    context = {
        'customer': customer_profile,
        'user': request.user,
    }
    return render(request, 'accounts/dashboard_customer.html', context)


@login_required
def manager_dashboard(request):
    """Salon manager dashboard."""
    if request.user.user_type != 'salon_manager':
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('accounts:login')
    
    manager_profile = request.user.manager_profile
    
    if not manager_profile.is_approved:
        return render(request, 'accounts/manager_pending_approval.html', {
            'manager': manager_profile
        })
    
    context = {
        'manager': manager_profile,
        'user': request.user,
    }
    return render(request, 'accounts/dashboard_manager.html', context)


@login_required
def stylist_dashboard(request):
    """Stylist dashboard."""
    if request.user.user_type != 'stylist':
        messages.error(request, 'دسترسی غیرمجاز')
        return redirect('accounts:login')
    
    stylist_profile = request.user.stylist_profile
    
    context = {
        'stylist': stylist_profile,
        'user': request.user,
    }
    context = {
        'stylist': stylist_profile,
        'user': request.user,
    }
    return render(request, 'accounts/dashboard_stylist.html', context)


@login_required
def dashboard_view(request):
    """Redirect to specific dashboard based on user type."""
    user = request.user
    if user.user_type == 'customer':
        return redirect('accounts:customer_dashboard')
    elif user.user_type == 'salon_manager':
        return redirect('accounts:manager_dashboard')
    elif user.user_type == 'stylist':
        return redirect('accounts:stylist_dashboard')
    elif user.user_type == 'site_admin':
        return redirect('admin:index')
    else:
        return redirect('accounts:customer_dashboard')


# ============================================================================
# API Views (DRF)
# ============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register_customer(request):
    """
    API endpoint for customer registration.
    
    POST /accounts/api/register/customer/
    Body: {phone_number, password, password_confirm, first_name, last_name, 
           selfie_photo, gender, date_of_birth}
    """
    serializer = CustomerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'ثبت‌نام با موفقیت انجام شد',
            'user_id': user.id,
            'phone_number': user.phone_number
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_register_manager(request):
    """
    API endpoint for salon manager registration.
    Requires admin approval.
    
    POST /accounts/api/register/manager/
    Body: {phone_number, password, password_confirm, salon_name, salon_photo,
           salon_address, salon_gender_type}
    """
    serializer = SalonManagerRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'ثبت‌نام ثبت شد. منتظر تأیید مدیر باشید',  # Pending approval
            'user_id': user.id,
            'phone_number': user.phone_number
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStylist])
def api_stylist_complete_profile(request):
    """
    API endpoint for stylist profile completion.
    
    POST /accounts/api/stylist/complete-profile/
    Body: {first_name, last_name, gender, date_of_birth}
    """
    try:
        stylist_profile = request.user.stylist_profile
    except AttributeError:
        return Response({'error': 'پروفایل آرایشگر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
    
    if not stylist_profile.is_temporary:
        return Response({'message': 'پروفایل قبلاً تکمیل شده است'}, status=status.HTTP_200_OK)
    
    serializer = StylistProfileCompletionSerializer(stylist_profile, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'پروفایل با موفقیت تکمیل شد',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsSiteAdmin])
def api_approve_manager(request, manager_id):
    """
    API endpoint for site admin to approve salon manager.
    
    POST /accounts/api/approve-manager/<manager_id>/
    """
    manager_profile = get_object_or_404(SalonManagerProfile, id=manager_id)
    
    if manager_profile.is_approved:
        return Response({'message': 'این مدیر قبلاً تأیید شده است'}, status=status.HTTP_200_OK)
    
    manager_profile.is_approved = True
    manager_profile.approved_at = timezone.now()
    manager_profile.approved_by = request.user
    manager_profile.save()
    
    return Response({
        'message': 'مدیر سالن تأیید شد',
        'manager_id': manager_profile.id,
        'salon_name': manager_profile.salon_name
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def api_pending_managers(request):
    """
    API endpoint to list pending salon manager approvals.
    
    GET /accounts/api/pending-managers/
    """
    pending_managers = SalonManagerProfile.objects.filter(is_approved=False)
    
    data = [{
        'id': m.id,
        'salon_name': m.salon_name,
        'phone_number': m.user.phone_number,
        'salon_gender_type': m.salon_gender_type,
        'created_at': m.created_at
    } for m in pending_managers]
    
    return Response({
        'count': len(data),
        'results': data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def api_get_csrf_token(request):
    """
    Ensure CSRF cookie is set.
    GET /accounts/api/csrf/
    """
    return Response({'detail': 'CSRF cookie set'})

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    JSON-based login for React Frontend.
    """
    username = request.data.get('phone_number') or request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'شماره تلفن و رمز عبور الزامی است'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        serializer = CustomUserSerializer(user)
        return Response({
            'detail': 'ورود موفقیت‌آمیز بود',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'شماره تلفن یا رمز عبور اشتباه است'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    JSON-based logout for React Frontend.
    """
    logout(request)
    return Response({'detail': 'خروج موفقیت‌آمیز بود'}, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_current_user(request):
    """
    Get current logged-in user details or update profile.
    
    GET /accounts/api/me/
    PATCH /accounts/api/me/ (multipart/form-data for photos)
    """
    if request.method == 'GET':
        serializer = CustomUserSerializer(request.user)
        data = serializer.data
        
        # Enrich data with specific profile fields for easier frontend routing
        user = request.user
        data['is_approved'] = False
        data['is_temporary'] = False
        data['profile_completed'] = False

        if user.user_type == 'salon_manager' and hasattr(user, 'manager_profile'):
            data['is_approved'] = user.manager_profile.is_approved
        elif user.user_type == 'stylist' and hasattr(user, 'stylist_profile'):
            data['is_temporary'] = user.stylist_profile.is_temporary
            data['profile_completed'] = not user.stylist_profile.is_temporary
            
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        user = request.user
        
        if user.user_type == 'customer' and hasattr(user, 'customer_profile'):
            serializer = CustomerProfileSerializer(user.customer_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(CustomUserSerializer(user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif user.user_type == 'salon_manager' and hasattr(user, 'manager_profile'):
            serializer = SalonManagerProfileSerializer(user.manager_profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(CustomUserSerializer(user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'error': 'Cannot update this profile type'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def api_admin_stats(request):
    """
    Get dashboard statistics for Site Admin.
    """
    from apps.salons.models import Salon
    from apps.appointments.models import Appointment
    
    today = timezone.now().date()
    
    stats = {
        'total_users': CustomUser.objects.count(),
        'total_customers': CustomUser.objects.filter(user_type='customer').count(),
        'total_stylists': CustomUser.objects.filter(user_type='stylist').count(),
        'total_managers': CustomUser.objects.filter(user_type='salon_manager').count(),
        'pending_managers': SalonManagerProfile.objects.filter(is_approved=False).count(),
        'total_salons': Salon.objects.count(),
        'active_salons': Salon.objects.filter(manager__is_approved=True).count(),
        'total_appointments': Appointment.objects.count(),
        'today_appointments': Appointment.objects.filter(appointment_date=today).count(),
    }
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsSiteAdmin])
def api_admin_users(request):
    """
    List all users for Site Admin management.
    Supports filtering by user_type.
    """
    user_type = request.GET.get('user_type')
    queryset = CustomUser.objects.all().order_by('-date_joined')
    
    if user_type:
        queryset = queryset.filter(user_type=user_type)
        
    # Use pagination
    paginator = generics.ListAPIView.pagination_class()
    paginated_users = paginator.paginate_queryset(queryset, request)
    serializer = CustomUserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsSiteAdmin])
def api_admin_user_detail(request, user_id):
    """
    Manage specific user:
    GET: Retrieve details
    PATCH: Update (e.g. is_active)
    DELETE: Remove user
    """
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
