from rest_framework.permissions import BasePermission
from rest_framework import permissions

from poolstore.models import PoolHouse, PoolHouseStaff


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser
    

class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        poolhouse_id = view.kwargs.get('poolhouse_pk')
        if poolhouse_id:
            try:
                poolhouse = PoolHouse.objects.get(id=poolhouse_id)
                staff_member = PoolHouseStaff.objects.filter(poolhouse=poolhouse, user=request.user).first()
                if staff_member or request.method in permissions.SAFE_METHODS:
                    return True
            except PoolHouse.DoesNotExist:
                return False
        return False
    

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
        poolhouse_id = view.kwargs.get('poolhouse_pk')
        if poolhouse_id:
            try:
                poolhouse = PoolHouse.objects.get(id=poolhouse_id)
                staff_member = PoolHouseStaff.objects.filter(poolhouse=poolhouse, user=request.user).first()
                if staff_member:
                    return True
            except PoolHouse.DoesNotExist:
                return False
        return False
    

class IsPlayerReservingUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.player_reserving.user == request.user