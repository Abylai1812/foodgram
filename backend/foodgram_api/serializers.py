"""Сериализаторы для API для проекта Foodgram.

Модуль содержит сериализаторы для преобразования моделей Django
в JSON-формат и обратно для REST API.
"""

import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from  .models import Recipes, Ingredients, Tags, Favorite, ShoppingCart
from users.models import User, Subscribe


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Ingredients` (ингредиенты для рецептов)."""


    class Meta:
        """Мета-класс для настройки сериализатора IngredientsSerializer."""

        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Tags` (теги для рецептов)."""


    class Meta:
        """Мета-класс для настройки сериализатора TagsSerializer."""

        model = Tags
        fields = ('name', 'slug')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Recipes` (рецепты блюд)."""

    #image = Base64ImageField(allow_null=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для настройки сериализатора RecipesSerializer."""

        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text', 'cooking_time', 'image', 'is_favorited')
        # fields = ('id', 'author', 'name', 'text', 'cooking_time', 'is_favorited')
        read_only_fields = ('author', 'is_favorited')

    # def __init__(self, *args, **kwargs):
    #     super(RecipesSerializer, self).__init__(*args, **kwargs)

    #     request = self.context.get('request')
    #     if request and request.method == 'PATCH':
    #         for field in 'tags', 'ingredients', 'image', 'name', 'text', 'cooking_time':
    #             self.fields[field].required = False
    
    def get_is_favorited(self, obj):
        """Метод настройки избранных для рецепта True/False.""" 
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False


class RecipesFavoriteSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения нужных полей рецепта для `Favorite,Subscribe`."""

    recipes = RecipesSerializer(read_only=True)

    class Meta:
        """Мета-класс для настройки сериализатора RecipesFavoriteSubscribeSerializer."""
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time', 'recipes')


class BaseUserSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для работы с пользователями."""

    class Meta:
        """Мета-класс для настройки сериализатора BaseUserSerializer."""

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar')
        read_only_fields = ('avatar',)


class CustomUserCreateSerializer(UserCreateSerializer, BaseUserSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields + ('password',)


class CustomUserSerializer(UserSerializer, BaseUserSerializer):

    class Meta(UserSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields


class UserAvatarSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для работы с аватаром пользователя."""
   
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        """Мета-класс для настройки сериализатора UserAvatarSerializer."""

        model = User
        fields=('avatar',)


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для работы с подпиской пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipesFavoriteSubscribeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()
    avatar = UserAvatarSerializer()


    class Meta:
        """Мета-класс для настройки сериализатора UserSubscribeSerializer."""

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 
            'is_subscribed', 'recipes', 'recipes_count', 'avatar')
        read_only_fields = ('recipes', 'avatar')
    

    def get_recipes_count(self, obj):
        """Метод настройки количества рецептов у автора."""
        return obj.recipes.count()
    
    def get_is_subscribed(self, obj):
        """Метод настройки подписки на пользователя True/False.""" 
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscribe.objects.filter(user=request.user, author=obj).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписок.

    Используется для получения все подписки пользователя
    и сделавшего запрос на пользователя.
    """

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    author = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )


    class Meta:
        """Мета-класс для настройки сериализатора SubscribeSerializer."""

        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        """Проверка валидации пользователя."""
        user = self.context['request'].user
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы подписаны на этого человека.'
            )
        
        return data


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """Сериализатор список покупок.

#     Используется для получения ингредиентов пользователя
#     для покупки.
#     """

#     ingredients = serializers.SerializersMethodField()

#     class Meta:
#         """Мета-класс для настройки сериализатора ShoppingCartSerializer."""

#         model = ShoppingCart
#         fields = ('ingredients',)

#     def get_ingredients(self):
#         ingredients = Recipes.objects.filter(ingredients=ingredients)
#         return ingredients


# class FavoriteSerializer(serializers.ModelSerializer): 
#     """Сериализатор избранное. Используется для добавление рецептов в избранное. """ 
#     user = serializers.SlugRelatedField(read_only=True, slug_field='username') 
#     recipes = RecipesFavoriteSubscribeSerializer(many=True) 
    
#     class Meta: 
#         """Мета-класс для настройки сериализатора FavoriteSerializer.""" 
#         model = Favorite 
#         fields = ('user', 'recipes') 
#         read_only_fields = ('user', 'recipes') 
        
#         def validate(self, data): 
#             """Проверка валидации избранных.""" 
#             user = self.context['request'].user 
#             recipes = data['recipes'] 
#             if Favorite.objects.filter(user=user, recipes=recipes).exists(): 
#                 raise serializers.ValidationError( 'Вы добавили этот рецепт в избранные.' ) 
#             return data

