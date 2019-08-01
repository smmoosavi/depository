from django.utils.translation import ugettext_lazy
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    message = ugettext_lazy("You are not Admin")

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.groups.filter(name="Admin").exists():
            return True
        return False
