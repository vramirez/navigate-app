from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit/delete objects.
    Read-only access is allowed for any request (including anonymous).
    """

    def has_permission(self, request, view):
        # Allow read operations for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write operations require authenticated admin user
        return request.user and request.user.is_authenticated and request.user.is_staff
