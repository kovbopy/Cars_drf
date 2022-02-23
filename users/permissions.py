from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("POST","GET","PATCH","PUT","DELETE") and \
           request.user.is_authenticated and \
           request.user.is_admin:
           return True
