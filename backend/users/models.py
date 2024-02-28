from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.validators import UnicodeUsernameValidator
from foodgram.constants import MAX_LENGTH_USER, MAX_LENGTH_EMAIL


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        'Email',
        max_length=MAX_LENGTH_EMAIL, unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_USER)
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_USER)
    username = models.CharField(
        'Никнейм',
        max_length=MAX_LENGTH_USER,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
    )

    class Meta:
        ordering = ('email',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_as_user',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_subscription'
        )]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} / {self.author}'
