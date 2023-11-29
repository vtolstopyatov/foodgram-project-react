from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    '''Модель ингредиентов.'''
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    '''Модель тегов.'''
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(
        max_length=7,
        unique=True,
        validators=[RegexValidator(
            regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Цвет должен быть в hex формате',
        )],
    )
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return f'{self.slug}'


class Recipe(models.Model):
    '''Модель рецептов.'''
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/images'
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1 минуты'
            ),
            MaxValueValidator(
                1440,
                message='Время приготовления не может быть больше 1440 минут'
            ),
        ],
    )
    followers = models.ManyToManyField(User,
                                       blank=True,
                                       through='Favorite')

    class Meta:
        ordering = ['-id']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return f'{self.name}'


class IngredientAmount(models.Model):
    '''Промежуточная модель ингредиентов и рецептов.'''
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Ингредиентов не может быть меньше 1'
            ),
            MaxValueValidator(
                2000, message='Ингредиентов не может быть больше 2000'
            ),
        ],
    )

    class Meta:
        verbose_name = 'amount of ingredients in recipe'
        verbose_name_plural = 'amount of ingredients in recipes'
        unique_together = ['ingredients', 'recipe']

    def __str__(self):
        return f'{self.ingredients.name}'


class ShoppingCart(models.Model):
    '''Модель списка покупок.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'shopping cart'
        verbose_name_plural = 'shopping carts'
        unique_together = ['user', 'recipe']


class Favorite(models.Model):
    '''Модель подписок.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        unique_together = ['user', 'recipe']
