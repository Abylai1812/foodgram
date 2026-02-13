"""Регистрация моделей в административной панели Django."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite,
    Ingredients,
    RecipeIngredient,
    Recipes,
    ShoppingCart,
    Subscribe,
    Tags,
    User,
)


class RecipesCountMixin:
    """Миксин для подсчета количества рецептов у объектов."""

    recipe_relation = 'recipes'

    def get_queryset(self, request):
        """Оптимизируем запрос к базе данных."""
        queryset = super().get_queryset(request)
        if self.recipe_relation:
            return queryset.annotate(
                rcount=Count(self.recipe_relation)
            )
        return queryset

    def get_recipes_count(self, instance):
        """Возвращает количества рецептов."""
        if not self.recipe_relation:
            return '-'
        return getattr(instance, 'rcount', 0)


@admin.register(User)
class ProfileUserAdmin(RecipesCountMixin, UserAdmin):
    """Настройка админ части пользователя."""

    list_display = (
        'id',
        'username',
        'email',
        'full_name',
        'avatar_preview',
        'recipes_count',
        'followers_count',
        'following_count'
    )
    list_display_links = ('username',)
    list_editable = ('email',)
    search_fields = ('username', 'email')
    ordering = ('username',)

    @admin.display(description='ФИО')
    def full_name(self, user):
        """Возваращает фамилия, имя пользователя."""
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Рецепты')
    def recipes_count(self, user):
        """Возвращает количества рецептов у пользователя."""
        return self.get_recipes_count(user)

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_preview(self, user):
        """Генерирует HTML-тег для отображения изображения аватара."""
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'style="width:60px; height:60px;" />'
            )
        return 'No avatar'

    @admin.display(description='Подписчики')
    def followers_count(self, user):
        """Возвращает количество подписчиков данного автора."""
        return user.author_subscriptions.count()

    @admin.display(description='Подписки')
    def following_count(self, user):
        """Возвращает количество подписок данного пользователя."""
        return user.subscriptions.count()


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
        'ingredients__name'
    )
    list_filter = ('tags', 'author')

    @admin.display(description='Фото')
    def image_recipe(self, recipe):
        """Генерирует HTML-тег для отображения изображения рецепта."""
        if recipe.image:
            return mark_safe(
                f'<img src="{recipe.image.url}" '
                f'style="width:100px; height:100px;" />'
            )
        return ''

    @admin.display(description='В избранных')
    def favorite_count(self, recipe):
        """Возвращает количества пользователей.

        Которые добавивших данный рецепт в избранное.
        """
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def tags_preview(self, recipe):
        """Возвращает строковое представление всех тегов рецепта."""
        tags = recipe.tags.all()
        return ', '.join(tag.name for tag in tags)

    @admin.display(description='Ингредиенты')
    def ingredients_preview(self, recipe):
        """Возвращает краткий перечень названий ингредиентов."""
        items = recipe.recipe_ingredients.select_related('ingredient')

        return mark_safe('<br>'.join(
            f'•{i.ingredient.name} - {i.amount} '
            f'{i.ingredient.measurement_unit}'
            for i in items
        ))


@admin.register(Ingredients)
class IngredientsAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройка админ части ингредиентов."""

    recipe_relation = 'recipe_ingredients'

    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)

    @admin.display(description='Количества в рецептах')
    def recipes_count(self, user):
        """Метод возвращает общее количества рецептов.

        У которых есть этот ингредиент.
        """
        return self.get_recipes_count(user)


@admin.register(Tags)
class TagsAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройка админ части тегов."""

    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')

    @admin.display(description='Количества в рецептах')
    def recipes_count(self, user):
        """Метод возвращает общее количества рецептов.

        У которых есть этот тег.
        """
        return self.get_recipes_count(user)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка админ части избранных."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('recipe__name', 'user__username')
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка админ части список покупок."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('recipe__name', 'user__username')
    list_filter = ('user',)


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """Настройка админ части подписок."""

    list_display = ('id', 'user', 'author')
    search_fields = ('author__username', 'user__username')
    list_filter = ('user',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка админ части подписок."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
