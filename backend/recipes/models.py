from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(max_length=256)
    measurement_unit = models.CharField(max_length=16)


class Tags(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/'
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    followers = models.ManyToManyField(User, related_name='favorite')


class IngredientsAmount(models.Model):
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='ingredients')
    amount = models.IntegerField()


# class Favorite(models.Model):
#     user = models.ForeignKey(
#         User,
#         models.CASCADE,
#         related_name='favorite',
#     )
#     recipe = models.ForeignKey(
#         Recipes,
#         models.CASCADE,
#         related_name='followers',
#     )


# class ShoppingBag(models.Model):
#     user = models.ForeignKey(
#         User,
#         models.CASCADE,
#         related_name='favorite',
#     )
#     recipes = models.ForeignKey(
#         Recipes,
#         models.CASCADE,
#         related_name='followers',
#     )
