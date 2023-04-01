from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartView, FavoriteView,
                    IngredientViewSet, RecipesViewSet,
                    ShoppingCartView, TagViewSet, UsersViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path(
        'recipes/<str:pk>/favorite/',
        FavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/<str:pk>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download_shopping_cart',
    ),
    path(
        '',
        include(router.urls),
    ),
    path(
        '',
        include('djoser.urls'),
    ),
    path(
        'auth/',
        include('djoser.urls.authtoken'),
    ),
]
