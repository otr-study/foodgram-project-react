from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.constraints import UniqueConstraint


class User(AbstractUser):
    email = models.EmailField('email', unique=True)
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_author',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions_subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'subscriber',),
                name='unique_subscription'
            ),
        )

    def __str__(self):
        return f'{self.subscriber} -> {self.author}'
