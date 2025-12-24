"""
URL configuration for Barber Shop project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # CAPTCHA URLs
    path('captcha/', include('captcha.urls')),
    
    # App URLs
    path('accounts/', include('apps.accounts.urls')),
    path('salons/', include('apps.salons.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('ratings/', include('apps.ratings.urls')),
    path('chat/', include('apps.chat.urls')),  # Chat APIs
    
    # Config API
    path('api/config/', include('config.api_urls')),
    
    # API URLs (if using DRF browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "مدیریت سیستم رزرو سالن"  # Persian: Salon Booking System Management
admin.site.site_title = "مدیریت سالن"  # Persian: Salon Management
admin.site.index_title = "خوش آمدید"  # Persian: Welcome
