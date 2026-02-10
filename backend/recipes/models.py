"""Модели для приложения recipes.

Содержит модели для рецептов, тегов, ингредиентов, избранное, список покупок, пользователей и подписок.
"""


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator


username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='Имя пользователя может содержать только буквы, цифры и символы',
    code='invalid_username'
)

class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField('Имя пользователя',
        max_length=150,
        unique=True,
        validators=[username_validator]
    )
    first_name = models.CharField('Имя', max_length=150, blank=False)
    last_name = models.CharField('Фамилия', max_length=150, blank=False)
    avatar = models.ImageField('Аватар', upload_to='users/', null=True, default=None)

    class Meta(AbstractUser.Meta):
        """Мета-класс для настройки модели CustomUser."""

        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает строковое представление имя пользователя."""
        return self.username


class Subscribe(models.Model):
    """Модель подписки пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscriptions',
        verbose_name='Автор'
    )

    class Meta:
        """Мета-класс для настройки модели Subscribe."""

        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]


class Tags(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField('Название', max_length=32, unique=True)
    slug = models.SlugField('Идентификатор', max_length=32, unique=True)

    class Meta:
        """Мета-класс для настройки модели Tags."""

        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает строковое представление тегов (название)."""
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов для рецептов."""

    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        """Мета-класс для настройки модели Tags."""

        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление ингредиентов (название)."""
        return self.name


class Recipes(models.Model):
    """Модель рецептов блюд."""

    name = models.CharField('Название', max_length=256)
    text = models.TextField('Текстовое описание')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    image = models.ImageField('Фото', upload_to='recipes/', blank=True, null=True)
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True
    )

    class Meta:
        """Мета-класс для настройки модели Recipes."""

        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает строковое представление рецептов (название)."""
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи Рецепта и Ингредиентов."""

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        'Количество', 
        validators=[MinValueValidator(1)]
    )

    class Meta:
        """Мета-класс для настройки модели RecipeIngredient."""

        verbose_name = 'Ингреденты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        """Возвращает строковое представление ингредиентов."""
        return f'{self.ingredient} {self.recipe}'


class UserRecipeRelation(models.Model):
    """Абстрактная модель для Избранных и Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_items'
        )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )

    class Meta:
        """Мета-класс для настройки модели UserRecipeRelation."""

        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_%(class)s'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление пользователя и рецепта."""
        return f'{self.user} {self.recipe}'


class Favorite(UserRecipeRelation):
    """Модель избранное."""

    class Meta(UserRecipeRelation.Meta):
        """Мета-класс для настройки модели Favorite."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipeRelation):
    """Модель список покупок."""

    class Meta(UserRecipeRelation.Meta):
        """Мета-класс для настройки модели ShoppingCart."""

        verbose_name = 'Список рецепта для покупки'
        verbose_name_plural = 'Списки рецептов для покупки'
