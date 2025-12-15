from django.urls import path
from . import views, api_views

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
]
