import base64
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers
from recipes.models import Recipes, Ingredients, IngredientsAmount, Tags

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = IngredientsAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True)
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = serializers.BooleanField(
        read_only=True,
        default=False,
    )

    class Meta:
        model = Recipes
        fields = (
            'id', 'name', 'tags', 'author', 'ingredients',
            'is_favorited',
            'text', 'cooking_time', 'image',
        )

    def to_representation(self, instance):
        user = self.context.get('request').user
        ret = super().to_representation(instance)
        if user.is_authenticated:
            ret['is_favorited'] = instance in user.favorite.all()
        return ret
    
    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(author=user, **validated_data)
        for ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=recipe,
                ingredients=ingredient.get('id'),
                amount=int(ingredient.get('amount'))
            )
        recipe.tags.set(tags)
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'cooking_time', 'image',)
