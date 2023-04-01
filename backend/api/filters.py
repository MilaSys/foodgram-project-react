from django.db import models
from django_filters import CharFilter, rest_framework

from recipes.models import Ingredient, Recipe


class IngredientFilter(rest_framework.FilterSet):
    """Фильтр ингредиентов."""

    name = CharFilter(method='filtering_by_name')

    def filtering_by_name(self, queryset, name, value):
        if not value:
            return queryset

        starts_with = queryset.filter(name__istartswith=value).annotate(
            qs_order=models.Value(0, models.IntegerField())
        )
        contains = (
            queryset.filter(name__icontains=value)
            .exclude(name__in=starts_with.values('name'))
            .annotate(qs_order=models.Value(1, models.IntegerField()))
        )

        return starts_with.union(contains).order_by('qs_order')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(rest_framework.FilterSet):
    """Фильтр рецептов."""
    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = rest_framework.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
