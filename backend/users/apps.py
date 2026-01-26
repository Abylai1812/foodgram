"""Регистрация приложении users."""


from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Настройка регистрации приложении users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
