from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient, Tag


class RecipeFilter(filters.FilterSet):
    '''Класс фильтров для предоставления Recipe.'''
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        conjoined=True,
    )
    author = filters.NumberFilter(
        field_name='author__pk',
        lookup_expr='exact',
    )
    is_favorited = filters.BooleanFilter(
        field_name='followers',
        method='in_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_cart',
        method='in_shopping_cart',
    )

    def in_favorited(self, queryset, name, value):
        if value and not self.request.user.is_authenticated:
            return queryset.none()
        if value:
            user = self.request.user
            return queryset.filter(followers=user)
        return queryset

    def in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_authenticated:
            return queryset.none()
        if value:
            user = self.request.user
            return queryset.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(filters.FilterSet):
    '''Класс фильтров для предоставления Ingredient.'''
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ['name']
