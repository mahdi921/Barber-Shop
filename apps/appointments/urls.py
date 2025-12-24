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
    path('api/approve/<int:appointment_id>/', views.approve_appointment, name='api_approve'),
    path('api/manage/list/<int:salon_id>/', views.get_salon_appointments, name='api_manager_list'),
    

]
