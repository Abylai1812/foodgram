"""Permissions(права доступа) для приложения foodgram_api.

Содержит permissions для рецептов, тегов и ингредиентов.
"""


from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Общепроектный пермишен для рецептов,подписки,избранные."""

    message = 'Изменение чужой записи запрещено!'


    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_staff
            or request.user.is_superuser
        )
