from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission

from .models import UserRole

class Forbidden404Exception(APIException):
    status_code = 404

class HospitalPermission(BasePermission):
    def has_permission(self, request, view):
        roles = UserRole.objects.filter(assigned_user=request.user).filter(hospital__isnull=False)
        if len(roles) == 0:
            raise Forbidden404Exception
        return True

class HospitalGroupPermission(BasePermission):
    def has_permission(self, request, view):
        roles = UserRole.objects.filter(assigned_user=request.user).filter(hospital_group__isnull=False)
        if len(roles) == 0:
            raise Forbidden404Exception
        return True

class SupplierPermission(BasePermission):
    def has_permission(self, request, view):
        roles = UserRole.objects.filter(assigned_user=request.user).filter(supplier__isnull=False)
        if len(roles) == 0:
            raise Forbidden404Exception
        return True

class SystemPermission(BasePermission):
    def has_permission(self, request, view):
        roles = UserRole.objects.filter(assigned_user=request.user).filter(system__isnull=False)
        if len(roles) == 0:
            raise Forbidden404Exception
        return True
