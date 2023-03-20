
from django.contrib.admin import ModelAdmin, TabularInline, register

from recipes.models import (
    FavoriteRecipe, Ingredient, IngredientAmount, Recipe, ShoppingCart, Tag
)
from recipes.strings import EMPTY


@register(Tag)
class TagAdmin(ModelAdmin):
    """Регистрация в админке тэгов."""

    list_display = ('name', 'color', 'slug')
    empty_value_display = f'{EMPTY}'
    ordering = ('color',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    """Настройки отображения таблицы с ингредиентами."""

    list_display = ('name', 'measurement_unit')
    empty_value_display = f'{EMPTY}'
    list_filter = ('name',)
    ordering = ('name',)


class IngredientAmountInline(TabularInline):
    model = IngredientAmount
    min_num = 1
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    """Настройки отображения таблицы с рецептами."""

    list_display = ('name', 'author')
    list_filter = ['author', 'name', 'tags']
    inlines = (IngredientAmountInline,)


@register(FavoriteRecipe)
class FavoriteRecipeAdmin(ModelAdmin):
    """Настройки отображения таблицы с избранными рецептами."""

    list_display = ('pk', 'user', 'recipe')
    empty_value_display = f'{EMPTY}'


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Настройки отображения таблицы с корзиной покупок."""
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = f'{EMPTY}'
