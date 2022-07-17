
from rest_framework import permissions


class IsAuthorOrReadOnlyOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
