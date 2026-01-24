"""Фильтрация для приложения foodgram_api.

Содержит настройку фильтрации для рецептов по тегам.
"""

import django_filters
from django_filters.rest_framework import filters
from foodgram_api.models import Recipes, Tags


class RecipeFilter(django_filters.FilterSet):
    """Настройка фильтрация рецептов по тегам, избранным, автору, спискам покупок"""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shoppping_cart = filters.BooleanFilter(method='filter_is_in_shoppping_cart')

    class Meta:
        """Мета-класс для настройки класса RecipeFilter."""
        model=Recipes
        fields = ('author', 'tags', 'is_favorited', 'is_in_shoppping_cart')
    
    def filter_is_favorited(self, queryset, name, value):
        """Метод фильтрации по избарнным."""
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shoppping_cart(self, queryset, name, value):
        """Метод фильтрации по спискам покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(in_carts__user=user)
        return queryset
