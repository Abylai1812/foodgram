"""Регистрация моделей в административной панели Django."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('username', )
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('username', 'email')
    ordering = ('username',)