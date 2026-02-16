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

    recipes_list_display = ('recipes_count',)

    def get_queryset(self, request):
        """Оптимизируем запрос к базе данных."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            recipes_count=Count('recipes')
        )

    @admin.display(description='Рецепты')
    def recipes_count(self, instance):
        """Возвращает количества рецептов."""
        return instance.recipes_count


@admin.register(User)
class ProfileUserAdmin(RecipesCountMixin, UserAdmin):
    """Настройка админ части пользователя."""

    list_display = (
        'id',
        'username',
        'email',
        'full_name',
        'avatar_preview',
        'followers_count',
        'following_count',
        *RecipesCountMixin.recipes_list_display
    )
    list_display_links = ('username',)
    fieldsets = (
        *UserAdmin.fieldsets,
        ('Аватар',
         {'fields': ('avatar_preview', 'avatar')})
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('email', 'avatar_preview')

    @admin.display(description='ФИО')
    def full_name(self, user):
        """ФИО пользователя."""
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_preview(self, user):
        """Генерирует HTML-тег для отображения изображения аватара."""
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'style="width:60px; height:60px;" />'
            )
        return ''

    @admin.display(description='Подписчики')
    def followers_count(self, user):
        """Возвращает количество подписчиков данного автора."""
        return user.author_subscriptions.count()

    @admin.display(description='Подписки')
    def following_count(self, user):
        """Возвращает количество подписок данного пользователя."""
        return user.subscriptions.count()


class RecipeIngredientInline(admin.TabularInline):
    """Позволяет добавлять/удалять ингредиенты в рецепте."""

    model = RecipeIngredient
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)
    min_num = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """Настройка админ части рецептов."""

    inlines = (RecipeIngredientInline,)

    list_display = (
        'id', 'name', 'author', 'tags_preview',
        'cooking_time', 'image_recipe',
        'ingredients_preview', 'favorite_count'
    )
    search_fields = (
        'name', 'tags__name',
        'author__username',
        'ingredients__name'
    )
    list_filter = ('tags', 'author')
    readonly_fields = ('image_recipe',)
    list_display_links = ('id', 'name',)

    @admin.display(description='Фото')
    @mark_safe
    def image_recipe(self, recipe):
        """Генерирует HTML-тег для отображения изображения рецепта."""
        if recipe.image:
            return (
                f'<img src="{recipe.image.url}" '
                f'style="width:100px; height:100px; '
                f'object-fit:cover; border-radius:5px" />'
            )
        return ''

    @admin.display(description='В избранных')
    def favorite_count(self, recipe):
        """Возвращает количества пользователей.

        Которые добавивших данный рецепт в избранное.
        """
        return recipe.favorites.count()

    @admin.display(description='Теги')
    @mark_safe
    def tags_preview(self, recipe):
        """Возвращает строковое представление всех тегов рецепта."""
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Ингредиенты')
    @mark_safe
    def ingredients_preview(self, recipe):
        """Возвращает краткий перечень названий ингредиентов."""
        return ('<br>'.join(
            f'•{i.ingredient.name} - {i.amount} '
            f'{i.ingredient.measurement_unit}'
            for i in recipe.recipe_ingredients.select_related('ingredient')
        ))


@admin.register(Ingredients)
class IngredientsAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройка админ части ингредиентов."""

    list_display = (
        'id', 'name', 'measurement_unit',
        *RecipesCountMixin.recipes_list_display
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(Tags)
class TagsAdmin(RecipesCountMixin, admin.ModelAdmin):
    """Настройка админ части тегов."""

    list_display = (
        'id', 'name', 'slug',
        *RecipesCountMixin.recipes_list_display,
    )
    search_fields = ('name', 'slug')


class FavoriteShoppingCartMixin:
    """Миксин для настройки избранных, список покупок."""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('recipe__name', 'user__username')
    list_filter = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(FavoriteShoppingCartMixin, admin.ModelAdmin):
    """Настройка админ части избранных."""

    pass


@admin.register(ShoppingCart)
class ShoppingCartAdmin(FavoriteShoppingCartMixin, admin.ModelAdmin):
    """Настройка админ части список покупок."""

    pass


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
