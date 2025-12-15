"""
Forms for user registration and authentication with CAPTCHA.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField
from .models import CustomUser, CustomerProfile, SalonManagerProfile, StylistProfile
from .validators import validate_iranian_phone


class CustomerRegistrationForm(UserCreationForm):
    """
    Registration form for customers with CAPTCHA.
    """
    # Customer-specific fields
    first_name = forms.CharField(
        max_length=50,
        label="نام",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام'})
    )
    last_name = forms.CharField(
        max_length=50,
        label="نام خانوادگی",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی'})
    )
    selfie_photo = forms.ImageField(
        label="عکس سلفی",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=CustomerProfile.GENDER_CHOICES,
        label="جنسیت",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        label="تاریخ تولد (میلادی)",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    # CAPTCHA
    captcha = CaptchaField(label="کد امنیتی")
    
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password1', 'password2']
        labels = {
            'phone_number': 'شماره تلفن',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09123456789'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'رمز عبور'})
        self.fields['password2'].label = 'تکرار رمز عبور'
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تکرار رمز عبور'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'customer'
        if commit:
            user.save()
            # Create customer profile
            CustomerProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                selfie_photo=self.cleaned_data['selfie_photo'],
                gender=self.cleaned_data['gender'],
                date_of_birth=self.cleaned_data['date_of_birth']
            )
        return user


class SalonManagerRegistrationForm(UserCreationForm):
    """
    Registration form for salon managers with CAPTCHA.
    Manager accounts require admin approval.
    """
    # Salon-specific fields
    salon_name = forms.CharField(
        max_length=100,
        label="نام سالن",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام سالن'})
    )
    salon_photo = forms.ImageField(
        label="عکس سالن",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    salon_address = forms.CharField(
        label="آدرس سالن",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'آدرس کامل سالن'})
    )
    salon_gender_type = forms.ChoiceField(
        choices=SalonManagerProfile.SALON_GENDER_CHOICES,
        label="نوع سالن",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # CAPTCHA
    captcha = CaptchaField(label="کد امنیتی")
    
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password1', 'password2']
        labels = {
            'phone_number': 'شماره تلفن',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09123456789'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].label = 'تکرار رمز عبور'
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'salon_manager'
        if commit:
            user.save()
            # Create manager profile (not approved yet)
            SalonManagerProfile.objects.create(
                user=user,
                salon_name=self.cleaned_data['salon_name'],
                salon_photo=self.cleaned_data['salon_photo'],
                salon_address=self.cleaned_data['salon_address'],
                salon_gender_type=self.cleaned_data['salon_gender_type'],
                is_approved=False
            )
        return user


class LoginForm(forms.Form):
    """
    Phone-based login form with CAPTCHA.
    """
    phone_number = forms.CharField(
        max_length=11,
        label="شماره تلفن",
        validators=[validate_iranian_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09123456789'
        })
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        })
    )
    captcha = CaptchaField(label="کد امنیتی")


class StylistProfileCompletionForm(forms.ModelForm):
    """
    Form for temporary stylists to complete their profile on first login.
    """
    class Meta:
        model = StylistProfile
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'gender': 'جنسیت',
            'date_of_birth': 'تاریخ تولد',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
