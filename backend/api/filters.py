from django_filters import rest_framework as filters

from recipes.models import Recipes, Ingredients


class RecipesFilter(filters.FilterSet):
    """
    Класс фильтров для предоставления Recipes.
    """
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='exact',
    )
    author = filters.CharFilter(
        field_name='author__pk',
        lookup_expr='exact',
    )
    # name = filters.CharFilter(
    #     field_name='name',
    #     lookup_expr='contains',
    # )
    # year = filters.CharFilter(
    #     field_name='year',
    #     lookup_expr='contains',
    # )

    class Meta:
        model = Recipes
        fields = ['tags', 'author']


class IngredientsFilter(filters.FilterSet):
    """
    Класс фильтров для предоставления Ingredients.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='contains',
    )

    class Meta:
        model = Ingredients
        fields = ['name']