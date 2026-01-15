"""ViewSet'ы для API для проекта Foodgram.

Модуль содержит ViewSet'ы для обработки CRUD операций
с рецептами, ингредиентами, тегами и пользователями через REST API.
"""


from io import BytesIO
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



from .serializers import (
    RecipesSerializer,
    IngredientsSerializer,
    TagsSerializer,
    UserAvatarSerializer,
    SubscribeSerializer,
    UserSubscribeSerializer,
    RecipesFavoriteSubscribeSerializer,
    )
from .models import Recipes, Ingredients, Tags, Favorite, ShoppingCart, RecipeIngredient
from users.models import Subscribe, User



class RecipesViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами.

    Обеспечивает CRUD операции для модели Recipes с проверкой прав автора.
    """

    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer

    def perform_create(self, serializer):
        """Автоматически назначает автора."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Метод настройки избранных добавление и удаление."""
        current_user = request.user
        recipe = get_object_or_404(Recipes, pk=self.kwargs['pk'])

        favorite = Favorite.objects.filter(user=current_user, recipe=recipe)

        if request.method == 'POST':
            if favorite.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorite.objects.create(user=current_user, recipe=recipe)
            serializer = RecipesFavoriteSubscribeSerializer(recipe, context={'request':request})
            return Response(serializer.data)
            
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этот рецепт не найден в избранным'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def post_delete_cart(self, request, pk=None):
        """Метод настройки список покупок добавление и удаление рецепта."""
        current_user = request.user
        recipe = get_object_or_404(Recipes, pk=self.kwargs['pk'])

        cart = ShoppingCart.objects.filter(user=current_user, recipe=recipe)

        if request.method == 'POST':
            if cart.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в список покупок'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=current_user, recipe=recipe)
            serializer = RecipesFavoriteSubscribeSerializer(recipe, context={'request':request})
            return Response(serializer.data)
            
        if cart.exists():
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Этот рецепт не найден в списке покупок'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
  
    def get_shopping_ingredients(self, request):
        """Формирует словарь ингредиентов для список текущего пользователя."""
        current_user = request.user

        cart_ingredients = {}
        for cart_entry in current_user.cart_recipes.all():
            recipe_ingredients = RecipeIngredient.objects.filter(recipes=cart_entry.recipe)
            for item in recipe_ingredients:
                name = item.ingredients.name
                amount = item.amount
                measurement_unit = item.ingredients.measurement_unit
                if name in cart_ingredients:
                    cart_ingredients[name]['amount'] += amount
                else:
                    cart_ingredients[name] = {
                        'amount': amount,
                        'measurement_unit': measurement_unit
                    }
        return cart_ingredients

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок пользователя в нужном формате."""
        cart_ingredients = self.get_shopping_ingredients(request)

        lines = []
        for name, info in cart_ingredients.items():
            lines.append(f'{name}({info["measurement_unit"]})—{info["amount"]}')
        cart_text = '\n'.join(lines)

        file_format = request.query_params.get('file_format', 'txt')
        file_name = f"shopping_cart.{file_format}"
        if  file_format == 'pdf':
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            y = 800
            for line in cart_text.split('\n'):
                p.drawString(50, y, line)
                y -= 20
            p.showPage()
            p.save()
            buffer.seek(0)
            response = HttpResponse(cart_text, content_type='application/pdf')
        elif file_format == 'txt':
            response = HttpResponse(cart_text, content_type='text/plain')
        elif file_format == 'csv':
            response = HttpResponse(cart_text, content_type='text/csv')
        
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами.

    Обеспечивает CRUD операции для модели Ingredients.
    """

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами.

    Обеспечивает CRUD операции для модели Tags.
    """

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer



class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями.

    Обеспечивает CRUD операции для модели User.
    """

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Метод настройки аватара добавление и удаление."""
        user = request.user
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserAvatarSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def get_subscriptions(self, request):
        """Метод настройки подписки."""
        subscriptions = User.objects.filter(subscribers__user=request.user)
        serializer = UserSubscribeSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def post_delete_subscription(self, request, id=None):
        """Метод настройки подписки."""
        current_user = request.user
        author = get_object_or_404(User, id=self.kwargs['id'])

        if request.method == 'POST':
            data = {'author': author}
            serializer = SubscribeSerializer(data=data, context={'request': request})
            if serializer.is_valid(): 
                serializer.save(user=current_user)
                return Response(
                    UserSubscribeSerializer(author, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        subscription = Subscribe.objects.filter(user=current_user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
