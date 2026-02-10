"""Модуль которая работаетс списком покупок.

Формирует словарь ингредиентов и возвращает отформатированную строку.
"""


from django.utils import timezone
from django.db.models import Sum
from django.template.loader import render_to_string

from recipes.models import RecipeIngredient, ShoppingCart


def get_shopping_ingredients(user):
    """Формирует словарь ингредиентов.

    Для список покупок текущего пользователя.
    """
    cart_ingredients = RecipeIngredient.objects.filter(
        recipe__shoppingcart_set__user=user).values(
        'ingredient__name', 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount')).order_by('ingredient__name')

    return cart_ingredients


def formatting_shoppinglist(request):
    """Функция принимает данные списка покупок.

    Возвращает отформатированную строку.
    """
    ingredients = get_shopping_ingredients(request.user)
    recipes = ShoppingCart.objects.filter(
        user=request.user
    ).select_related('recipe__author')

    context = {
        'user': request.user,
        'ingredients': ingredients,
        'date': timezone.now().date(),
        'recipes': recipes
    }

    return render_to_string(
        'shopping_list.txt',
        context
    )
