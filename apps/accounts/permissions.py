"""
Custom DRF permissions for role-based access control.
"""
from rest_framework import permissions


class IsCustomer(permissions.BasePermission):
    """Permission check for customers only."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'customer'


class IsSalonManager(permissions.BasePermission):
    """Permission check for salon managers only."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'salon_manager'


class IsApprovedSalonManager(permissions.BasePermission):
    """Permission check for approved salon managers only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.user_type != 'salon_manager':
            return False
        
        try:
            return request.user.manager_profile.is_approved
        except AttributeError:
            return False


class IsStylist(permissions.BasePermission):
    """Permission check for stylists only."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'stylist'


class IsSiteAdmin(permissions.BasePermission):
    """Permission check for site admins only."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.user_type == 'site_admin' or request.user.is_superuser
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the owner
        return obj.user == request.user
