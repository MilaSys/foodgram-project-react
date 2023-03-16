import django.contrib.auth.password_validation as validate
from django.contrib.auth import authenticate
from djoser.serializers import UserCreateSerializer
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from users.models import Subscription
from users.admin import User


class CustomUserRegSerializer(UserCreateSerializer):
    """
    Регистрация пользователя.
    """

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
    """
    Аутентификация.
    """
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


class SubscribeMixin:
    """Отображает наличие/отсутствие подписки на автора."""
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, args):
        user_id = args.id if isinstance(args, User) else args.author.id
        request_user = self.context.get('request').user.id
        queryset = Subscription.objects.filter(
            author=user_id,
            user=request_user
        ).exists()

        return queryset


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализация модели с подписками."""

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message=('Вы уже подписанны на данного автора!')
            )
        ]

    def validate_following(self, args):
        if args == self.context['request'].user:
            raise serializers.ValidationError(
                "Кажется вы хотите подписаться на самого себя!"
            )

        return args


class CustomUserSerializer(
        SubscribeMixin,
        serializers.ModelSerializer
    ):
    is_subscribed = serializers.BooleanField(read_only=True)

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
