"""Модели для приложения foodgram_api.

Содержит модели для рецептов, тегов и ингредиентов.
"""


from django.db import models

from users.models import User


class Tags(models.Model):
    """Модель тегов для рецептов."""

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Слаг', max_length=100)


    class Meta:
        """Мета-класс для настройки модели Tags."""

        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_name_slug'
            )
        ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает строковое представление тегов (название)."""
        return self.name


class Ingredients(models.Model):
    """Модель ингредиентов для рецептов."""

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Количества', max_length=10)


    class Meta:
        """Мета-класс для настройки модели Tags."""

        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление ингредиентов (название)."""
        return self.name


class Recipes(models.Model):
    """Модель рецептов блюд."""

    name = models.CharField('Название', max_length=200)
    text = models.TextField('Текстовое описание')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    image = models.ImageField(upload_to='foodgram_api/', blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredients, through='RecipeIngredient', related_name='recipes')
    tags = models.ManyToManyField(Tags, related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления в минутах')
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

    recipes = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    """Модель избранное."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='favorite_recipe')


    class Meta:
        """Мета-класс для настройки модели Favorite."""

        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """Модель список покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_recipes')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='cart_user')


    class Meta:
        """Мета-класс для настройки модели ShoppingCart."""

        verbose_name = 'Список покупок'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart'
            )
        ]