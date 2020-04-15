from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission

from .models import User

class Forbidden404Exception(APIException):
    status_code = 404

def usertype_permissions(request, user_type):
    permission = request.user and request.user.user_type == user_type.name
    if not permission:
        raise Forbidden404Exception
    return True

class HospitalPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, User.UserType.Hospital)

class HospitalGroupPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, User.UserType.HospitalGroup)

class SupplierPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, User.UserType.Supplier)

class SystemPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, User.UserType.System)