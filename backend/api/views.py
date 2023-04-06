from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from djoser.views import UserViewSet
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


from .filters import IngredientFilter, RecipeFilter
from .paginations import LimitPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscribeCreateSerializer, SubscribeSerializer,
                          TagSerializer)
from users.models import Subscription, User


class CreateUserView(UserViewSet):
    """Кастомизация пользователя из Djoser."""

    serializer_class = CustomUserSerializer

    def get_queryset(self):
        return User.objects.all()


class UsersViewSet(UserViewSet):
    """
    Создание/получение пользователей
    и
    создание/получение/удаления подписок.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    pagination_class = LimitPagination
    http_method_names = ['get', 'post', 'delete', 'head']

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)

        return super().get_permissions()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthorOrAdminOrReadOnly]
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        data = {
            'user': user.id,
            'author': id,
        }

        if request.method == 'POST':
            serializer = SubscribeCreateSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription, user=user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthorOrAdminOrReadOnly])
    def subscriptions(self, request):
        user = request.user
        subscribe = User.objects.filter(idol__user=user)
        page = self.paginate_queryset(subscribe)
        serializer = SubscribeSerializer(
            page, many=True,
            context={'request': request})

        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Тэги."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    """Ингредиенты."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """Создание/удаление/вывод рецептов."""

    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete', 'patch']
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer

        return RecipeReadSerializer

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={
                    'user': user.id,
                    'recipe': pk
                },
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(views.APIView):
    """Добавление/удаление рецепта в избранное."""

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]

    def post(self, request, pk=None):
        user = request.user
        data = {'user': user.id, 'recipe': pk, }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = FavoriteRecipe.objects.filter(user=user, recipe=recipe)

        if not instance:
            return Response(
                {'error': 'Этого рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartView(views.APIView):
    """Добавление/удаление рецепта в корзину."""

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]

    def post(self, request, pk=None):

        user = request.user
        data = {'user': user.id, 'recipe': pk, }
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if not instance:
            return Response(
                {'error': 'Этого рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCartView(views.APIView):
    """Скачивание списка покупок."""

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]

    def get(self, request):
        items = IngredientAmount.objects.select_related('recipe', 'ingredient')
        items = items.filter(recipe__shopping_cart__user=request.user)

        items = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename{filename}'

        return response
