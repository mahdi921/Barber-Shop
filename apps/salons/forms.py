from django import forms
from .models import Service, WorkingHours
from apps.accounts.models import CustomUser, StylistProfile

class StylistCreationForm(forms.Form):
    phone_number = forms.CharField(max_length=11, label='شماره تلفن')
    first_name = forms.CharField(max_length=30, label='نام')
    last_name = forms.CharField(max_length=30, label='نام خانوادگی')
    gender = forms.ChoiceField(choices=[('male', 'مرد'), ('female', 'زن')], label='جنسیت')
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if CustomUser.objects.filter(username=phone).exists():
            raise forms.ValidationError('این شماره تلفن قبلاً ثبت شده است')
        return phone

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_type', 'custom_name', 'price', 'duration_minutes', 'stylist']
        labels = {
            'service_type': 'نوع خدمت',
            'custom_name': 'نام سفارشی',
            'price': 'قیمت (تومان)',
            'duration_minutes': 'مدت زمان (دقیقه)',
            'stylist': 'آرایشگر (اختیاری - اگر انتخاب نکنید برای همه است)'
        }
    
    def __init__(self, salon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stylist'].queryset = StylistProfile.objects.filter(salon=salon)

