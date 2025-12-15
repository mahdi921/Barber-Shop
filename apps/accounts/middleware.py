"""
Middleware for checking temporary stylist profile completion.

Redirects temporary stylists to profile completion page on first login.
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class StylistProfileCompletionMiddleware(MiddlewareMixin):
    """
    Middleware to ensure temporary stylists complete their profile.
    
    If a stylist logs in with is_temporary=True, they are redirected
    to the profile completion page for all requests except:
    - The completion page itself
    - Logout
    - Static/media files
    - Admin pages
    """
    
    def process_request(self, request):
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None
        
        # Skip for superusers and staff
        if request.user.is_superuser or request.user.is_staff:
            return None
        
        # Check if user is a temporary stylist
        if request.user.user_type == 'stylist':
            try:
                stylist_profile = request.user.stylist_profile
                
                # If temporary and not on allowed pages, redirect to completion
                if stylist_profile.is_temporary:
                    allowed_paths = [
                        reverse('accounts:stylist_complete_profile'),
                        reverse('accounts:logout'),
                        '/static/',
                        '/media/',
                        '/admin/',
                    ]
                    
                    # Check if current path is allowed
                    path = request.path
                    if not any(path.startswith(allowed) for allowed in allowed_paths):
                        return redirect('accounts:stylist_complete_profile')
            
            except AttributeError:
                # Stylist profile doesn't exist
                pass
        
        return None
