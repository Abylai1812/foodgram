"""Сериализаторы для API для проекта Foodgram.

Модуль содержит сериализаторы для преобразования моделей Django
в JSON-формат и обратно для REST API.
"""

import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredients,
    RecipeIngredient,
    Recipes,
    ShoppingCart,
    Tags,
    Subscribe, User
)
from api.constans import MIN_COOKING_TIME



class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений, закодированных в Base64."""

    def to_internal_value(self, data):
        """Преобразует строку Base64 в файл изображения."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class BaseUserSerializer(UserSerializer):
    """Кастомный сериализатор для работы с пользователями."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для настройки сериализатора BaseUserSerializer."""

        model = User
        fields = UserSerializer.Meta.fields + (
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, author):
        """Метод настройки подписки на пользователя True/False."""
        request = self.context.get('request')
        return request and request.user.is_authenticated and Subscribe.objects.filter(
            user=request.user, author=author).exists()


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Ingredients` (ингредиенты для рецептов)."""

    class Meta:
        """Мета-класс для настройки сериализатора.

        IngredientsSerializer.
        """

        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientsReadSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для чтение записи ингредиентов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        """Мета-класс для настройки сериализатора.

        IngredientReadSerializer.
        """

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class IngredientsAmountSerilaizer(serializers.Serializer):
    """Вспомогательный сериализатор ингредиента для создание рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    amount = serializers.IntegerField(min_value=MIN_COOKING_TIME)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Tags` (теги для рецептов)."""

    class Meta:
        """Мета-класс для настройки сериализатора TagsSerializer."""

        model = Tags
        fields = ('id', 'name', 'slug')


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтение модели `Recipes` (рецепты блюд)."""

    is_favorited = serializers.SerializerMethodField()
    author = BaseUserSerializer(read_only=True)
    ingredients = IngredientsReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    tags = TagsSerializer(many=True, read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для настройки сериализатора.

        RecipesReadSerializer.
        """

        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'text', 'cooking_time'
        )
        read_only_fields = fields

    def get_user_recipe_status(self, obj, model):
        """Вспомогательный метод для проверки.

        Есть ли рецепт в избарнных и списке покупок.
        """
        request = self.context.get('request')
        return request and request.user.is_authenticated and model.objects.filter(
            user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        """Метод настройки избранных для рецепта True/False."""
        return self.get_user_recipe_status(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        """Метод настройки список покупок для рецепта True/False."""
        return self.get_user_recipe_status(obj, ShoppingCart)


class RecipesCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создание и обновление модели.

    `Recipes` (рецепты блюд).
    """

    image = Base64ImageField(allow_null=False)
    ingredients = IngredientsAmountSerilaizer(many=True)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME)

    class Meta:
        """Мета-класс для настройки сериализатора.

        RecipesCreateUpdateSerializer.
        """

        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image',
            'name', 'text', 'cooking_time'
        )
    
    def check_duplicates(items, field_name):
        """Проверяет список на дубли и показывает все повторяющиеся значения."""
        duplicates = sorted({item for item in items if items.count(item) > 1})
        if duplicates:
            raise serializers.ValidationError(
                f'{field_name} не должны повторяться: {duplicates}.'
            )

    def validate(self, data):
        """Метод валидации ингредиентов и тегов."""
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        if ingredients is None:
            raise serializers.ValidationError(
                'Ошибка.Нет поле ingredients.'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Список ingredients не может быть пустым.'
            )

        id_values = [item['id'] for item in ingredients]
        check_duplicates(id_values, 'Ингредиенты')

        if tags is None:
            raise serializers.ValidationError(
                'Ошибка.Нет поле tags.'
            )
        check_duplicates(tags, 'Теги')

        return data

    def create_ingredients_set(self, recipe, ingredients):
        """Вспомогательный метод для создание ингредиентов."""
        ingredients_list = [
            RecipeIngredient(
                ingredient=item['id'],
                amount=item['amount'],
                recipe=recipe
            ) for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients_list)

        return recipe

    def create(self, validated_data):
        """Метод для сохранение ингредиентов и тегов."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = super().create(validated_data)

        recipe.tags.set(tags_data)

        self.create_ingredients_set(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        """Метод для обновление рецепта."""
        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)
        
        instance = super().update(instance, validated_data)

        instance.tags.set(tags_data)

        instance.recipe_ingredients.delete()
        self.create_ingredients_set(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        """Возвращаем данные через сериализатор для чтения после POST/PATCH."""
        return RecipesReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения нужных полей.

    Рецепта для `Favorite,Subscribe`.
    """

    class Meta:
        """Мета-класс для настройки сериализатора.

        ShortRecipeSerializer
        """

        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserAvatarSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для работы с аватаром пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Мета-класс для настройки сериализатора UserAvatarSerializer."""

        model = User
        fields = ('avatar',)


class AuthorWithRecipesSerializer(BaseUserSerializer):
    """Кастомный сериализатор для работы с подпиской пользователя."""

    recipes = ShortRecipeSerializer(many=True)
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        """Мета-класс для настройки сериализатора AuthorWithRecipesSerializer."""

        model = User
        fields = BaseUserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = ('recipes', 'avatar')
