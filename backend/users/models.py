from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q, F


class User(AbstractUser):
    '''Кастомная модель пользователя'''
    verbose_name = 'user'
    verbose_name_plural = 'users'
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Follow(models.Model):
    '''Модель для подписки на пользователей'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'follow'
        verbose_name_plural = 'follows'
        unique_together = ['user', 'author']
        constraints = [
            CheckConstraint(
                check=~Q(user__exact=F('author')),
                name='check_user_not_author',
            ),
        ]
