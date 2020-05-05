from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
from django.db.models import Q

from .models import UserRole

class Forbidden404Exception(APIException):
    status_code = 404

def usertype_permissions(request, user_type):
    lastUsedRole = UserRole.get_default_role(request.user)

    if user_type == 'Hospital':
        roles = UserRole.objects.filter(assigned_user=request.user).filter(hospital__isnull=False)
        isSameRoleLastUsed = lastUsedRole != None and lastUsedRole.hospital != None
    elif user_type == 'Hospital Group':
        roles = UserRole.objects.filter(assigned_user=request.user).filter(hospital_group__isnull=False)
        isSameRoleLastUsed = lastUsedRole != None and lastUsedRole.hospital_group != None
    elif user_type == 'Supplier':
        roles = UserRole.objects.filter(assigned_user=request.user).filter(supplier__isnull=False)
        isSameRoleLastUsed = lastUsedRole != None and lastUsedRole.supplier != None
    elif user_type == 'System':
        roles = UserRole.objects.filter(assigned_user=request.user).filter(system__isnull=False)
        isSameRoleLastUsed = lastUsedRole != None and lastUsedRole.system != None
    elif user_type == 'Hospital|Hospital Group':
        roles = UserRole.objects.filter(assigned_user=request.user).filter(Q(hospital__isnull=False) | Q(hospital_group__isnull=False))
        isSameRoleLastUsed = lastUsedRole != None and (lastUsedRole.hospital != None or lastUsedRole.hospital_group != None)

    if len(roles) == 0:
        raise Forbidden404Exception
    elif not isSameRoleLastUsed:
        UserRole.make_default_role(request.user, roles.first())

    currentRole = UserRole.get_default_role(request.user)

    if currentRole.hospital:
        userType = 'Hospital'
    elif currentRole.hospital_group:
        userType = 'Hospital Group'
    elif currentRole.supplier:
        userType = 'Supplier'
    else:
        userType = 'System'

    request.user.set_current_type(userType)
    return True

class HospitalPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, 'Hospital')

class HospitalGroupPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, 'Hospital Group')

class SupplierPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, 'Supplier')

class SystemPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, 'System')

class HospitalSharedPermission(BasePermission):
    def has_permission(self, request, view):
        return usertype_permissions(request, 'Hospital|Hospital Group')
