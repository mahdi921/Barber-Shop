"""
URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Template-based views
    path('register/customer/', views.register_customer_view, name='register_customer'),
    path('register/manager/', views.register_manager_view, name='register_manager'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Stylist profile completion
    path('stylist/complete-profile/', views.stylist_complete_profile_view, name='stylist_complete_profile'),
    
    # Dashboards
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
    path('dashboard/stylist/', views.stylist_dashboard, name='stylist_dashboard'),
    
    # API endpoints
    path('api/register/customer/', views.api_register_customer, name='api_register_customer'),
    path('api/register/manager/', views.api_register_manager, name='api_register_manager'),    # API URLs
    path('api/csrf/', views.api_get_csrf_token, name='api_csrf'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/stylist/complete-profile/', views.api_stylist_complete_profile, name='api_stylist_complete_profile'),
    path('api/approve-manager/<int:manager_id>/', views.api_approve_manager, name='api_approve_manager'),
    path('api/pending-managers/', views.api_pending_managers, name='api_pending_managers'),
    path('api/admin/stats/', views.api_admin_stats, name='api_admin_stats'),
    path('api/admin/users/', views.api_admin_users, name='api_admin_users'),
    path('api/admin/users/<int:user_id>/', views.api_admin_user_detail, name='api_admin_user_detail'),
    path('api/me/', views.api_current_user, name='api_current_user'),
    
    # Profile update endpoints
    path('api/profile/customer/', __import__('apps.accounts.profile_api_views', fromlist=['update_customer_profile']).update_customer_profile, name='update_customer_profile'),
    path('api/profile/stylist/', __import__('apps.accounts.profile_api_views', fromlist=['update_stylist_profile']).update_stylist_profile, name='update_stylist_profile'),
    path('api/profile/manager/', __import__('apps.accounts.profile_api_views', fromlist=['update_manager_profile']).update_manager_profile, name='update_manager_profile'),
]
