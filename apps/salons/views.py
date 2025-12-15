from django.shortcuts import render, get_object_or_404
from .models import Salon

def salon_list(request):
    """
    List of all approved salons.
    Enforces gender-based visibility for customers.
    """
    salons = Salon.objects.approved()
    
    if request.user.is_authenticated and request.user.user_type == 'customer':
        try:
            gender = request.user.customer_profile.gender
            salons = salons.for_gender(gender)
        except AttributeError:
            # Fallback if profile issue, though shouldn't happen for valid customers
            pass
            
    return render(request, 'salons/salon_list.html', {'salons': salons})

def salon_detail(request, pk):
    """Detail view for a salon."""
    salon = get_object_or_404(Salon, pk=pk)
    # Filter out temporary (incomplete profile) stylists
    stylists = salon.stylists.filter(is_temporary=False)
    return render(request, 'salons/salon_detail.html', {'salon': salon, 'stylists': stylists})

# ============================================================================
# Management Views
# ============================================================================
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .forms import StylistCreationForm, ServiceForm
from apps.accounts.models import CustomUser, StylistProfile

@login_required
def manage_stylists(request):
    """
    Manage salon stylists.
    """
    if request.user.user_type != 'salon_manager':
        return redirect('accounts:login')
    
    salon = request.user.manager_profile.salons.first()
    if not salon:
        messages.error(request, 'شما هیچ سالنی ندارید')
        return redirect('accounts:manager_dashboard')
        
    stylists = salon.stylists.all()
    
    if request.method == 'POST':
        form = StylistCreationForm(request.POST)
        if form.is_valid():
            # Create User
            user = CustomUser.objects.create_user(
                phone_number=form.cleaned_data['phone_number'],
                password='temp_password_123',  # Should be generated or sent via SMS
                user_type='stylist'
            )
            # Create Profile
            StylistProfile.objects.create(
                user=user,
                salon=salon,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                gender=form.cleaned_data['gender'],
                is_temporary=True  # Force profile completion
            )
            messages.success(request, 'آرایشگر با موفقیت اضافه شد. رمز عبور پیش‌فرض: temp_password_123')
            return redirect('salons:manage_stylists')
    else:
        form = StylistCreationForm()
        
    return render(request, 'salons/manage_stylists.html', {'form': form, 'stylists': stylists})

@login_required
def manage_services(request):
    """
    Manage salon services.
    """
    if request.user.user_type != 'salon_manager':
        return redirect('accounts:login')
        
    salon = request.user.manager_profile.salons.first()
    if not salon:
        return redirect('accounts:manager_dashboard')

    services = salon.services.all()
    
    if request.method == 'POST':
        form = ServiceForm(salon, request.POST)
        form.instance.salon = salon  # Set salon on instance before validation
        if form.is_valid():
            form.save() # salon is already on instance
            messages.success(request, 'خدمت با موفقیت اضافه شد')
            return redirect('salons:manage_services')
    else:
        form = ServiceForm(salon)
        
    return render(request, 'salons/manage_services.html', {'form': form, 'services': services})
