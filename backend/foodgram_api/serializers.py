"""Сериализаторы для API для проекта Foodgram.

Модуль содержит сериализаторы для преобразования моделей Django
в JSON-формат и обратно для REST API.
"""


import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram_api.models import Recipes, Ingredients, Tags, Favorite, RecipeIngredient, ShoppingCart
from users.models import User, Subscribe


class BaseUserSerializer(serializers.ModelSerializer):
    """Кастомный сериализатор для работы с пользователями."""

    class Meta:
        """Мета-класс для настройки сериализатора BaseUserSerializer."""

        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar', )
        read_only_fields = ('avatar',)


class CustomUserCreateSerializer(UserCreateSerializer, BaseUserSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields + ('password',)


class CustomUserSerializer(UserSerializer, BaseUserSerializer):

    class Meta(UserSerializer.Meta):
        model = User
        fields = BaseUserSerializer.Meta.fields


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Ingredients` (ингредиенты для рецептов)."""


    class Meta:
        """Мета-класс для настройки сериализатора IngredientsSerializer."""

        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class IngredientsReadSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для чтение записи ингредиентов."""

    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(source='ingredients.measurement_unit')
    amount = serializers.IntegerField()


    class Meta:
        """Мета-класс для настройки сериализатора IngredientReadSerializer."""

        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsAmountSerilaizer(serializers.Serializer):
    """Вспомогательный сериализатор ингредиента для создание рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели `Tags` (теги для рецептов)."""


    class Meta:
        """Мета-класс для настройки сериализатора TagsSerializer."""

        model = Tags
        fields = ('id', 'name', 'slug')


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтение модели `Recipes` (рецепты блюд)."""

    image = Base64ImageField(allow_null=False)
    is_favorited = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsReadSerializer(many=True)
    # is_in_shopping_cart = serializers.SerializerMethodField()


    class Meta:
        """Мета-класс для настройки сериализатора RecipesReadSerializer."""

        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'image',
            'is_favorited', 'name', 'text', 'cooking_time')
        read_only_fields = ('author', 'is_favorited')
    

    def get_is_favorited(self, obj):
        """Метод настройки избранных для рецепта True/False.""" 
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False
    
    # def get_is_in_shopping_cart(self, obj):
    #     """Метод настройки список покупок для рецепта True/False."""
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
    #     return False



class RecipesCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создание и обновление модели `Recipes` (рецепты блюд)."""

    image = Base64ImageField(allow_null=False)
    ingredients = IngredientsAmountSerilaizer(many=True)

    class Meta:
        """Мета-класс для настройки сериализатора RecipesCreateUpdateSerializer."""

        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'image',
                'name', 'text',  'cooking_time')
        read_only_fields = ('author',)

    def create_ingredients_set(self, recipes, ingredients):
        """Вспомогательный метод для создание ингредиентов."""
        for item in ingredients:
           RecipeIngredient.objects.create(
               ingredients=item['id'],
               amount=item['amount'],
               recipes=recipes
            )

        return recipes

    def create(self, validated_data):
        """Метод для сохранение ингредиентов и тегов."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipes.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        self.create_ingredients_set(recipe, ingredients_data)

        return recipe
    
    def update(self, instance, validated_data):
        """Метод для обновление рецепта."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        tags_data = validated_data.pop('tags', None)
        ingredients_data = validated_data.pop('ingredients', None)

        if tags_data is not None:
            instance.tags.set(tags_data)
        instance.save()

        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipes=instance).delete()
            self.create_ingredients_set(instance, ingredients_data)

        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Возвращаем данные через сериализатор для чтения после POST/PATCH."""
        return RecipesReadSerializer(instance, context=self.context).data


class RecipesFavoriteSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения нужных полей рецепта для `Favorite,Subscribe`."""

    recipes = RecipesReadSerializer(read_only=True)

    class Meta:
        """Мета-класс для настройки сериализатора RecipesFavoriteSubscribeSerializer."""
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time', 'recipes')


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

