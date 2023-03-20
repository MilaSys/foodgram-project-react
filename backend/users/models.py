from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    """Модель таблицы пользователей.
    Attributes:
        email: EmailField - переопределяем поле, выставляем
        ограничение символов согласно тз
        first_name: CharField - переопределяем поле, выставляем
        ограничение символов согласно тз
    """

    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Subscription(models.Model):
    """Модель таблицы подписчиков.
    Attributes:
        user: ForeignKey - ссылка (ID) на объект класса User
        author: ForeignKey - ссылка (ID) на объект класса User
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='idol',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='subscriber_not_author',
            )
        ]

    def __str__(self):
        return f'The {self.user} is subscribed to the {self.author}'
