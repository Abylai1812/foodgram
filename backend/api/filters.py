"""Фильтрация для приложения foodgram_api.

Содержит настройку фильтрации для рецептов по тегам.
"""

import django_filters
from django_filters.rest_framework import filters

from recipes.models import Recipes, Tags


class RecipeFilter(django_filters.FilterSet):
    """
    Настройка фильтрация рецептов.

    По тегам, избранным, автору, спискам покупок.
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        """Мета-класс для настройки класса RecipeFilter."""

        model = Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, favorites, name, value):
        """Метод фильтрации по избарнным."""
        user = self.request.user
        if value and user.is_authenticated:
            favorites = favorites.filter(favorite_set__user=user)
        return favorites

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод фильтрации по спискам покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(shoppingcart_set__user=user)
        return queryset
