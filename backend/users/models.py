from django.contrib.auth.models import AbstractUser
from django.db import models


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
