"""ViewSet'ы для API для проекта Foodgram.

Модуль содержит ViewSet'ы для обработки CRUD операций
с рецептами, ингредиентами, тегами и пользователями через REST API.
"""


from io import BytesIO
from reportlab.pdfgen import canvas


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from django.urls import reverse

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny


from foodgram_api.serializers import (
    RecipesCreateUpdateSerializer,
    RecipesReadSerializer,
    IngredientsSerializer,
    TagsSerializer,
    UserAvatarSerializer,
    SubscribeSerializer,
    UserSubscribeSerializer,
    RecipesFavoriteSubscribeSerializer,
    )
from foodgram_api.models import Recipes, Ingredients, Tags, Favorite, ShoppingCart, RecipeIngredient
from users.models import Subscribe, User
from foodgram_api.permissions import IsAuthorOrReadOnly
from foodgram_api.pagination import BasePagination
from foodgram_api.filters import RecipeFilter



class RecipesViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами.

    Обеспечивает CRUD операции для модели Recipes с проверкой прав автора.
    """

    queryset = Recipes.objects.all().order_by('-pub_date')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Определение сериализаторов при определенных запросах."""
        if self.request.method in 'GET':
            return RecipesReadSerializer
        return RecipesCreateUpdateSerializer

    def perform_create(self, serializer):
        """Автоматически назначает автора."""
        serializer.save(author=self.request.user)

    def create_or_delete_relation(self, request, model=None):
        """
        Всмогомательный метод для сокращения дублирования кода 
        при добавлении/удалении рецептов из избранного или корзины пользователя. 
        """
        current_user = request.user
        recipe = get_object_or_404(Recipes, pk=self.kwargs['pk'])

        relation = model.objects.filter(user=current_user, recipe=recipe)

        if request.method == 'POST':
            if relation.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            model.objects.create(user=current_user, recipe=recipe)
            serializer = RecipesFavoriteSubscribeSerializer(recipe, context={'request': request})
            return Response(serializer.data)

        if relation.exists():
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Метод настройки избранных добавление и удаление."""
        return self.create_or_delete_relation(
            request, 
            model=Favorite
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def post_delete_cart(self, request, pk=None):
        """Метод настройки в список покупок добавление и удаление."""
        return self.create_or_delete_relation(
            request,
            model=ShoppingCart
        )

    def get_shopping_ingredients(self, request):
        """Формирует словарь ингредиентов для список покупок текущего пользователя."""
        current_user = request.user

        cart_ingredients = {}
        for cart_entry in current_user.cart_items.all():
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

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Метод получение короткий ссылки на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(
            f'/r/{recipe.id}/'
        )
        return Response({
            'short-link': short_link
        })

def redirect_to_recipe(request, pk):
    """Перенаправляет с короткой ссылки на страницу рецепта."""
    get_object_or_404(Recipes, pk=pk)
    return redirect(f'{settings.FRONTEND_URL}recipes/{pk}/')


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами.

    Обеспечивает CRUD операции для модели Ingredients.
    """

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        """Метод поиска ингредиенты по полю name регистронезависимо, по вхождению в начало названия."""
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с тегами.

    Обеспечивает CRUD операции для модели Tags.
    """

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    """ViewSet для работы с пользователями.

    Обеспечивает CRUD операции для модели User.
    """

    queryset = User.objects.all()
    permission_classes = [AllowAny]

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
        """Метод настройки получение всех подписчиков."""
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscribeSerializer(
                page,
                many=True,
                context={'reuest':request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscribeSerializer(
            queryset,
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
