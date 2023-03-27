import django.contrib.auth.password_validation as validate
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers

import base64

from recipes.models import (FavoriteRecipe, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from users.admin import User
from users.models import Subscription


class Base64ImageField(serializers.ImageField):
    """Кодирование/декодирование изображения в/из формата Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserRegSerializer(UserCreateSerializer):
    """Регистрация пользователя."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, password):
        validate.validate_password(password)

        return password


class CustomAuthTokenSerializer(serializers.Serializer):
    """Аутентификация."""

    email = serializers.EmailField(
        label='Email',
        write_only=True
    )
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label='Токен',
        read_only=True
    )

    def validate(self, args):
        email = args.get('email')
        password = args.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                message = 'Проверьте корректность введенных данных.'
                raise serializers.ValidationError(
                    message,
                    code='authorization',
                )

        else:
            message = 'Поля email и пароль, обязательны для заполнения.'
            raise serializers.ValidationError(
                message,
                code='authorization'
            )

        args['user'] = user

        return args


class RecipeShortSerializer(serializers.ModelSerializer):
    """Мини-сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UsersSerializer(UserSerializer):
    """Отображение информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, args):
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=user, author=args.id
        ).exists()


class SubscribeSerializer(UsersSerializer):
    """Добавление/удаление/просмотр подписок."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, args):
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = args.recipes.all()

        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]

        return RecipeShortSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, args):
        return args.recipes.count()


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


class RecipeReadSerializer(serializers.ModelSerializer):
    """Вывод рецептов/рецепта для чтения."""

    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = UsersSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientsEditSerializer(
        many=True,
        required=True,
        source='amount_ingredient'
    )
    is_favorited = serializers.BooleanField(
        read_only=True
    )
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True
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
