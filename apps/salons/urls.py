from django.urls import path
from . import views, api_views
from .management_api_views import (
    api_manager_salon, api_manager_services, api_manager_service_detail,
    api_manager_working_hours, api_manager_working_hours_detail,
    # New endpoints
    api_manager_salons, api_manager_salon_detail,
    api_manager_salon_stylists, api_manager_stylist_detail
)

app_name = 'salons'

urlpatterns = [
    path('', views.salon_list, name='salon_list'),
    path('<int:pk>/', views.salon_detail, name='salon_detail'),
    
    # Management URLs
    path('manage/stylists/', views.manage_stylists, name='manage_stylists'),
    path('manage/services/', views.manage_services, name='manage_services'),

    # API URLs
    path('api/list/', api_views.SalonListAPIView.as_view(), name='api_salon_list'),
    path('api/<int:pk>/', api_views.SalonDetailAPIView.as_view(), name='api_salon_detail'),
    
    # Manager Dashboard API URLs - Multi-Salon Support
    path('api/manager/salons/', api_manager_salons, name='api_manager_salons'),
    path('api/manager/salons/<int:salon_id>/', api_manager_salon_detail, name='api_manager_salon_detail_new'),
    path('api/manager/salons/<int:salon_id>/stylists/', api_manager_salon_stylists, name='api_manager_salon_stylists'),
    path('api/manager/stylists/<int:stylist_id>/', api_manager_stylist_detail, name='api_manager_stylist_detail'),
    
    # Legacy Manager Dashboard API URLs (for backward compatibility)
    path('api/manager/salon/', api_manager_salon, name='api_manager_salon'),
    path('api/manager/services/', api_manager_services, name='api_manager_services'),
    path('api/manager/services/<int:service_id>/', api_manager_service_detail, name='api_manager_service_detail'),
    path('api/manager/working-hours/', api_manager_working_hours, name='api_manager_working_hours'),
    path('api/manager/working-hours/<int:hours_id>/', api_manager_working_hours_detail, name='api_manager_working_hours_detail'),
]
