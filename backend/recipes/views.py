"""ViewSet'ы для recipes для проекта Foodgram.

Модуль содержит ViewSet'ы для обработки CRUD операций.
"""


from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipes


def redirect_to_recipe(request, pk):
    """Перенаправляет с короткой ссылки на страницу рецепта."""
    recipe = get_object_or_404(Recipes, pk=pk)
    return redirect(f'/recipes/{recipe.id}/')
