from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    '''Модель ингредиентов'''
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=16)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    '''Модель тегов'''
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.slug}'


class Recipe(models.Model):
    '''Модель рецептов'''
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
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    followers = models.ManyToManyField(User,
                                       related_name='favorite',
                                       blank=True)

    def __str__(self):
        return f'{self.name}'


class IngredientAmount(models.Model):
    '''Промежуточная модель ингредиентов и рецептов'''
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f'{self.ingredients.name}'


class ShoppingCart(models.Model):
    '''Модель списка покупок'''
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
