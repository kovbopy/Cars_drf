from rest_framework import permissions


class CarPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("POST", "PATCH", "PUT", "DELETE") and \
           request.user.is_authenticated and request.user.is_admin:
            return True

        elif request.method == "GET" and request.user.is_authenticated:
            return True
