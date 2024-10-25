from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser
    

class IsCurrentUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user
        

class IsRaterOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.rater.user == request.user
    

class IsStaffOrDenied(BasePermission):
    """
    Custom permission to only allow staff members to access the view.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
    

class IsPlayerReservingUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.player_reserving.user == request.user