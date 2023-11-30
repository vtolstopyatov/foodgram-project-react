from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    '''Viewset модели Recipe.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminUser | AuthorOrReadOnly,)

    def create_relation(self, request, model, serializer_class):
        '''Создаёт отношение между объектом запроса и моделью.'''
        recipe = self.get_object()
        user = request.user
        verbose_name = model._meta.verbose_name
        if model.objects.filter(user=user, recipe=recipe):
            return Response(
                {'errors': f'already in {verbose_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = serializer_class(
            recipe,
            context={'request': request}
        )
        f = model.objects.create(user=user, recipe=recipe)
        f.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_relation(self, request, model):
        '''Удаляет отношение между объектом запроса и моделью.'''
        recipe = self.get_object()
        user = request.user
        relations = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if relations:
            relations.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        verbose_name = model._meta.verbose_name
        return Response(
            {'errors': f'not in {verbose_name}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk=None):
        '''Добавляет рецепт в избранное.'''
        response = self.create_relation(
            request,
            model=Favorite,
            serializer_class=FavoriteSerializer
        )
        return response

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        '''Удаляет рецепт из избранного.'''
        response = self.delete_relation(
            request,
            model=Favorite,
        )
        return response

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        '''Возвращает файл списка покупок.'''
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipes = []
        for i in shopping_cart:
            recipes.append(i.recipe)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(Sum('amount'))
        to_file = ['Список покупок:\n'.encode('utf-8')]
        for i in ingredients:
            name = i.get('ingredients__name')
            amount = i.get('amount__sum')
            measurment_unit = i.get('ingredients__measurement_unit')
            to_file.append(
                f'{name} — {amount} {measurment_unit}\n'.encode('utf-8')
            )
        file = BytesIO()
        file.writelines(to_file)
        file.seek(0)
        response = FileResponse(
            file,
            as_attachment=True,
            filename='shopping_cart.txt'
        )
        return response

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        '''Добавляет рецепт в список покупок.'''
        response = self.create_relation(
            request,
            model=ShoppingCart,
            serializer_class=ShoppingCartSerializer
        )
        return response

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        '''Удаляет рецепт из списка покупок.'''
        response = self.delete_relation(
            request,
            model=ShoppingCart,
        )
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset модели Ingredient.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset модели Tag.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class UserViewSet(DjoserUserViewSet):
    '''Viewset модели User.'''
    serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(
        detail=False, methods=['get'],
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request, *args, **kwargs):
        '''Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты.
        '''
        user = request.user
        pages = self.paginate_queryset(
            User.objects.filter(following__user=user).order_by('pk')
        )
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post'],
            permission_classes=(IsAuthenticated,),)
    def subscribe(self, request, id=None):
        '''Подписаться на пользователя.'''
        author = self.get_object()
        user = request.user
        if user.follower.filter(user=user, author=author):
            return Response(
                {'errors': 'already in subscribed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            return Response(
                {'errors': 'subscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        f = Follow.objects.create(user=user, author=author)
        f.save()
        serializer = SubscriptionSerializer(
            author, context={'request': request},
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        '''Отписаться от пользователя.'''
        author = self.get_object()
        user = request.user
        if user.follower.filter(user=user, author=author):
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'not subscribed'},
            status=status.HTTP_400_BAD_REQUEST
        )
