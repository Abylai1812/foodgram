"""Пагинация для приложения foodgram_api.

Содержит настройки пагинации для рецептов и пользователей.
"""


from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """Базовая настройка пагинации."""

    page_size = 6
    page_size_query_param = 'limit'