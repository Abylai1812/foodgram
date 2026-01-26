"""Регистрация приложении foodgram_api."""


from django.apps import AppConfig


class FoodgramApiConfig(AppConfig):
    """Настройка регистрации приложении foodgram_api."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodgram_api'
    verbose_name = 'Рецепты'
