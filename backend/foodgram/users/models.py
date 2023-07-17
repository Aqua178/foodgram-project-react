from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.mixins import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']
    username = models.CharField(
        max_length=settings.LENGTH150,
        unique=True,
        verbose_name='Ник пользователя',
        validators=[validate_username]
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.LENGTH254,
        unique=True,
    )

    first_name = models.CharField(
        max_length=settings.LENGTH150,
        verbose_name='Имя пользователя',
    )
    last_name = models.CharField(
        max_length=settings.LENGTH150,
        verbose_name='Фамилия пользователя',
    )

    password = models.CharField(
        _('password'),
        max_length=settings.LENGTH150,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_fields'
            ),
        ]

    def __str__(self):
        return self.username
