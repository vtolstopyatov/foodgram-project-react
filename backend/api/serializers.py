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


class IngredientsAmountSerializer(serializers.ModelSerializer):
    amount = serializers.ModelField(model_field=IngredientsAmount()._meta.get_field('amount'))
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
    
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)
    

    class Meta:
        model = IngredientsAmount
        fields = (
            'amount',
            'id',
            'name',
            'measurement_unit',
        )

class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    ingredients = IngredientsAmountSerializer(many=True)
    # ingredients = IngredientsAmountSerializer()
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipes
        fields = (
            'name', 'ingredients', 'tags',
            'text', 'cooking_time', 'image',
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipes.objects.create(author=user, **validated_data)
        for ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipes=recipe,
                ingredients=ingredient.get('id'),
                amount=int(ingredient.get('amount'))
            )
        recipe.tags.set(tags)
        return recipe


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)
