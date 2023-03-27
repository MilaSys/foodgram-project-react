from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework

from djoser.views import UserViewSet
from rest_framework import status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.admin import User
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .paginations import LimitPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CustomAuthTokenSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer, UsersSerializer)


class CustomAuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = CustomAuthTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CustomAuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({'token': str(token)}, status=status.HTTP_201_CREATED)


class Logout(APIView):
    """Сброс токена."""

    def post(self, request):
        request.user.auth_token.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersViewSet(UserViewSet):
    """
    Создание/получение пользователей
    и
    создание/получение/удаления подписок.
    """

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPagination
    http_method_names = ['get', 'post', 'delete', 'head']

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)

        return super().get_permissions()

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, author=author
        )

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': f'Вы уже подписанны на {author}!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user == author:
                return Response(
                    {'error': 'Нельзя подписаться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            Subscription.objects.create(user=user, author=author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                {'error': f'Вы не подписаны на {author}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, permission_classes=[IsAuthenticated])
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
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if object.exists():
                object.delete()

                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                {'error': 'Этого рецепта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )


class FavoriteView(views.APIView):
    """Добавление/удаление рецепта в избранное."""

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]

    def post(self, request, pk=None):
        user = request.user
        data = {'user': user.id, 'recipe': pk, }
        context = {'request': request}
        serializer = FavoriteSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

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
        context = {'request': request}
        serializer = ShoppingCartSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

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
        items = IngredientAmount.objects.select_related(
            'recipe', 'ingredient'
        )
        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session['purchases']
            )

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
