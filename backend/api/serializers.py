import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    """Кодирование/декодирование изображения в/из формата Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IsSubscription(metaclass=serializers.SerializerMetaclass):
    """Отображение наличия/отсутствия подписки пользователем на автора."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, args):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=request.user, author__id=args.id
        ).exists()


class IsRecipe(metaclass=serializers.SerializerMetaclass):
    """Отображение наличия/отсутствия рецептов в избранном и корзине."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, args):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return FavoriteRecipe.objects.filter(
            user=request.user, recipe__id=args.id
        ).exists()

    def get_is_in_shopping_cart(self, args):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=args.id
        ).exists()


class IsRecipeCount(metaclass=serializers.SerializerMetaclass):
    """Отображение количества рецептов автора."""

    recipes_count = serializers.SerializerMethodField()

    def get_recipes_count(self, args):
        return Recipe.objects.filter(author__id=args.id).count()


class CustomUserSerializer(UserCreateSerializer, IsSubscription):
    """Кастомизация пользователя из Djoser."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        write_only_fields = ('password', )
        read_only_fields = ('id', )
        extra_kwargs = {'is_subscribed': {'required': False}}

    def to_representation(self, args):
        result = super(CustomUserSerializer, self).to_representation(args)
        result.pop('password', None)

        return result


class RecipeShortSerializer(serializers.ModelSerializer):
    """Мини-сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(CustomUserSerializer, IsRecipeCount):
    """Отображение подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + \
            ('recipes', 'recipes_count')

    def get_recipes(self, args):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = args.recipes.all()

        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]

        return RecipeShortSerializer(queryset, context=context, many=True).data


class SubscribeCreateSerializer(CustomUserSerializer):
    """Создание подписки"""
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на Автора.',
            )
        ]

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST
            )

        return data

    def create(self, validated_data):
        subscription = Subscription.objects.create(**validated_data)

        return subscription

    def to_representation(self, instance):
        return SubscribeSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Тэг."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ингредиент."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        order_by = ('-name',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Ингредиенты для отображения в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientsEditSerializer(serializers.ModelSerializer):
    """Ингредиенты для рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание/изменение рецепта."""

    image = Base64ImageField(
        max_length=None,
        use_url=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientsEditSerializer(
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data['ingredients']
        ingredient_list = []

        for items in ingredients:
            ingredient = get_object_or_404(Ingredient, id=items['id'])

            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient} уже добавлен в рецепт!'
                )

            ingredient_list.append(ingredient)
        tags = data['tags']

        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!'
            )

        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!'
                )

        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления не должно быть менее 1 минуты!'
            )

        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте ингредиент для вашего рецепта!'
            )

        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше либо равно 1!'
                )

        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)

        if 'tags' in validated_data:
            instance.tags.set(validated_data.pop('tags'))

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeReadSerializer(serializers.ModelSerializer, IsRecipe):
    """Вывод рецептов/рецепта для чтения."""

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientInRecipeSerializer(
        many=True,
        required=True,
        source='amount_ingredient'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавления рецепта в избранное."""

    name = serializers.CharField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.URLField(
        source='recipe.image.url',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        extra_kwargs = {
            'user': {'write_only': True},
            'recipe': {'write_only': True}
        }
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в избранное.',
            )
        ]

    def create(self, validated_data):
        subscription = FavoriteRecipe.objects.create(**validated_data)

        return subscription


class ShoppingCartSerializer(FavoriteSerializer):
    """Добавление рецепта в корзину."""

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже находится в списке покупок',
            )
        ]

    def create(self, validated_data):
        subscription = ShoppingCart.objects.create(**validated_data)

        return subscription
