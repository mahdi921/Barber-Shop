"""URL configuration for appointments app."""
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # API endpoints
    path('api/availability/', views.get_availability, name='api_availability'),
    path('api/book/', views.book_appointment, name='api_book'),
    path('api/my-appointments/', views.my_appointments, name='api_my_appointments'),
    path('api/cancel/<int:appointment_id>/', views.cancel_appointment, name='api_cancel'),
    
    # Template URLs
    path('book/', views.booking_view, name='booking_page'),
    path('list/', views.appointment_list_view, name='appointment_list'),
]
