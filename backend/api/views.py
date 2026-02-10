"""ViewSet'ы для API для проекта Foodgram.

Модуль содержит ViewSet'ы для обработки CRUD операций
с рецептами, ингредиентами, тегами и пользователями через REST API.
"""

from io import BytesIO
from django.http import FileResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from api.filters import RecipeFilter
from recipes.models import (
    Favorite, Ingredients,
    Recipes, ShoppingCart,
    Tags, Subscribe, User
)
from api.pagination import RecipePagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientsSerializer,
    RecipesCreateUpdateSerializer,
    ShortRecipeSerializer,
    RecipesReadSerializer,
    TagsSerializer,
    UserAvatarSerializer,
   AuthorWithRecipesSerializer
)
from recipes.utills.shopping_list import formatting_shoppinglist


class RecipesViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами.

    Обеспечивает CRUD операции для модели Recipes с проверкой прав автора.
    """

    queryset = Recipes.objects.all().order_by('-pub_date')
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = RecipePagination
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
        Вспомогомательный метод для сокращения дублирования кода.

        При добавлении/удалении рецептов из избранного
        или корзины пользователя.
        """
        current_user = request.user
        recipe_id = self.kwargs['pk']

        if request.method == 'DELETE':
            get_object_or_404(
                model,
                user=current_user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipe = get_object_or_404(Recipes, pk=recipe_id)
        _, created = model.objects.get_or_create(
            user=current_user,
            recipe=recipe
        )

        if not created:
            raise ValidationError(
                {'detail': f'Рецепт {recipe.name} уже добавлен в {model}.'}
            )

        return Response(ShortRecipeSerializer(
            recipe,
            context={'request': request}
        ).data, status=status.HTTP_201_CREATED)

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
            model=Favorite,
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

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивает список покупок пользователя в нужном формате."""

        file_format = request.query_params.get('file_format', 'txt')
       
        if file_format == 'txt':
            response = FileResponse(
                BytesIO(formatting_shoppinglist(request).encode('utf-8')),
                as_attachment=True,
                filename=f'shopping_cart.{file_format}'
            )

        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_short_link(self, request, pk=None):
        """Метод получение короткий ссылки на рецепт."""
        return Response({
            'short-link': request.build_absolute_uri(
            reverse('short_link_redirect', kwargs={'pk': pk})
            )
        })


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами.

    Обеспечивает CRUD операции для модели Ingredients.
    """

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['^name']


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

        serializer = UserAvatarSerializer(
            user,
            data=request.data,
            partial=True
        )
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
        queryset = User.objects.filter(author_subscriptions__user=request.user)
        page = self.paginate_queryset(queryset)
        
        serializer = AuthorWithRecipesSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def post_delete_subscription(self, request, id=None):
        """Метод настройки подписки."""
        current_user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'DELETE':
            get_object_or_404(
                Subscribe,
                author=author,
                user=current_user
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        
        if current_user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')

        if Subscribe.objects.filter(
            user=current_user,
            author=author
        ).exists():
            raise ValidationError('Вы подписаны на этого человека.')
        
        Subscribe.objects.create(user=current_user, author=author)

        return Response(
            AuthorWithRecipesSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )
