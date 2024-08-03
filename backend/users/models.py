from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Моделька пользователя
    """
    username = models.CharField(
        ('Имя пользователя'),
        max_length=150,
        unique=True
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(
        'Почта',
        max_length=254,
        blank=False,
        unique=True
    )
    is_subscribed = models.BooleanField(
        'Подписка',
        blank=True,
        null=True,
        default=False
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatar_images/',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['username']
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='uniqie_username_email'
            )
        ]

    def __str__(self):
        return self.username
