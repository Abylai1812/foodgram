from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    avatar = models.ImageField(upload_to='users/', null=True, default=None)


    class Meta(AbstractUser.Meta):
        """Мета-класс для настройки модели CustomUser."""

        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Возвращает строковое представление имя пользователя."""
        return self.username


class Subscribe(models.Model):
    """Модель подписки пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )


    class Meta:
        """Мета-класс для настройки модели Subscribe."""

        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
