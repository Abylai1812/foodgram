"""Регистрация моделей в административной панели Django."""


from django.contrib import admin

from foodgram_api.models import Ingredients, Recipes, Tags


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Настройка админ части рецептов."""

    list_display = ('id', 'name', 'text', 'author', 'cooking_time')
    list_editable = ('name', 'text', 'author', 'cooking_time')
    search_fields = ('name', 'text', 'author',
                     'author__username', 'is_favorited')
    list_filter = ('tags',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Настройка админ части ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Настройка админ части тегов."""

    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name',)
