from collections import OrderedDict

from django.contrib.auth import get_user_model
from recipes.models import (Ingredient, IngredientAmount, Recipe, ShoppingCart,
                            Tag)
from rest_framework import serializers
from users.models import Follow

from .fields import Base64ImageField

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов.'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор пользователей.'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        '''Поле для отображения подписки на пользователя.'''
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(
                user=user,
                author=obj,
            ).exists()
        return False


class IngredientAmountSerializer(serializers.ModelSerializer):
    '''Сериализатор количества ингредиентов.'''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredients.pk')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор тегов.'''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagField(serializers.PrimaryKeyRelatedField):
    '''Поле кастомного представления тегов.'''

    def to_representation(self, value, pk=False):
        if pk:
            return value.id
        return TagSerializer(value, context={
            'request': self.context.get('request')
        }).data

    def get_choices(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        if cutoff is not None:
            queryset = queryset[:cutoff]

        return OrderedDict([
            (
                self.to_representation(item, pk=True),
                self.display_value(item)
            )
            for item in queryset
        ])


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов.'''
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'text', 'cooking_time', 'image',
        )

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('At least one tag required')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Tags must be unique')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'At least one ingredient required'
            )
        unique_ingredints = {
            ingredient['ingredients']['pk'] for ingredient in ingredients
        }
        if len(ingredients) != len(unique_ingredints):
            raise serializers.ValidationError('Ingredients must be unique')
        return ingredients

    def get_is_favorited(self, obj):
        '''Отображает, что рецепт в избранном.'''
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj in user.favorite.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Отображает, что рецепт в корзине.'''
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(recipe=obj, user=user).exists()
        return False

    def ingredients_create(self, recipe, ingredients):
        ingredients_amount = [IngredientAmount(
            recipe=recipe,
            ingredients=ingredient['ingredients']['pk'],
            amount=int(ingredient['amount']),
        ) for ingredient in ingredients]
        IngredientAmount.objects.bulk_create(ingredients_amount)

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.ingredients_create(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if ingredients := validated_data.get('ingredients'):
            IngredientAmount.objects.filter(recipe=instance).delete()
            self.ingredients_create(instance, ingredients)
        if tags := validated_data.get('tags'):  # ЛОВИ МОРЖЕЙ!!!!!1
            instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор избранного.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов для сериализатора подписок.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    '''Сериализатор подписок.'''
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        '''Получает объекты для поля recipes'''
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            queryset = Recipe.objects.filter(
                author=obj)[:int(recipes_limit)]
        else:
            queryset = obj.recipes
        serializer = SubscriptionRecipeSerializer(
            instance=queryset, many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj).count()
        return count


class ShoppingCartSerializer(RecipeSerializer):
    '''Сериализатор списка покупок.'''

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
