"""Регистрация моделей в административной панели Django."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from recipes.models import User, Ingredients, Recipes, Tags


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    """Настройка админ части пользователя."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar_preview',
        'recipes_count',
        'followers_count',
        'following_count'
    )
    list_display_links = ('username', )
    list_editable = ('first_name', 'last_name', 'email')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def avatar_preview(self, obj):
        """Генерирует HTML-тег для отображения изображения аватара."""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" '
                f'style="width:60px; height:60px;" />'
            )
        return 'No avatar'

    def recipes_count(self, obj):
        """Возвращает общее количество рецептов пользователя."""
        return obj.recipes.count()

    def followers_count(self, obj):
        """Возвращает количество подписчиков данного автора."""
        return obj.author_subscriptions.count()

    def following_count(self, obj):
        """Возвращает количество подписок данного пользователя."""
        return obj.subscriptions.count()

    recipes_count.short_description = 'Рецепты'
    avatar_preview.short_description = 'Аватар'
    followers_count.short_description = 'Подписчики'
    following_count.short_description = 'Подписки'


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Настройка админ части рецептов."""

    list_display = (
        'id', 'name', 'text', 'author', 'tags_preview',
        'cooking_time', 'image_recipe', 'favorite_count',
        'ingredients_preview'
    )
    search_fields = (
        'name', 'tags__name',
        'author__username',
        'recipe_ingredients__ingredient__name'
    )
    list_filter = ('tags', 'author')

    def image_recipe(self, obj):
        """Генерирует HTML-тег для отображения изображения рецепта."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                f'style="width:100px; height:100px;" />'
            )
        return 'No image'

    def favorite_count(self, obj):
        """Возвращает количества пользователей.

        Которые добавивших данный рецепт в избранное.
        """
        return obj.favorite_set.count()

    def tags_preview(self, obj):
        """Возвращает строковое представление всех тегов рецепта."""
        tags = obj.tags.all()
        return ', '.join(tag.name for tag in tags)

    def ingredients_preview(self, obj):
        """Возвращает краткий перечень названий ингредиентов."""
        items = obj.recipe_ingredients.select_related('ingredient')

        return mark_safe('<br>'.join(
            f'•{i.ingredient.name} - {i.amount} '
            f'{i.ingredient.measurement_unit}'
            for i in items
        ))

    image_recipe.short_description = 'Фото'
    favorite_count.short_description = 'В избранных'
    tags_preview.short_description = 'Теги'
    ingredients_preview.short_description = 'Ингредиенты'


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Настройка админ части ингредиентов."""

    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    def recipes_count(self, obj):
        """Метод возвращает общее количества рецептов.

        В которых есть этот ингредиент.
        """
        return obj.ingredient_recipes.count()

    recipes_count.short_description = 'Количества в рецептах'


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    """Настройка админ части тегов."""

    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')

    def recipes_count(self, obj):
        """Метод возвращает общее количества рецептов.

        В которых есть этот тег.
        """
        return obj.recipes.count()

    recipes_count.short_description = 'Количества в рецептах'
