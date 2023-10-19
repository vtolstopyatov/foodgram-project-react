from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from recipes.models import (Ingredient, IngredientAmount, Recipe, ShoppingCart,
                            Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    '''Viewset модели Recipe.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [AuthorOrReadOnly]

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = [IsAdminUser]
        elif self.action == 'favorite':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'favorite_delete':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'download_shopping_cart':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'shopping_cart':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'shopping_cart_delete':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        '''Добавляет рецепт в избранное.'''
        recipe = self.get_object()
        user = request.user
        if recipe.followers.filter(pk=user.pk):
            return Response(
                {'errors': 'already in favorites'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FavoriteSerializer(recipe, context={'request': request})
        recipe.followers.add(user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        '''Удаляет рецепт из избранного.'''
        recipe = self.get_object()
        user = request.user
        if recipe.followers.filter(pk=user.pk):
            recipe.followers.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'not in favorites'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
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

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        '''Добавляет рецепт в список покупок.'''
        recipe = self.get_object()
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=recipe):
            return Response(
                {'errors': 'already in shopping cart'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ShoppingCartSerializer(
            recipe,
            context={'request': request}
        )
        f = ShoppingCart.objects.create(user=user, recipe=recipe)
        f.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        '''Удаляет рецепт из списка покупок.'''
        recipe = self.get_object()
        user = request.user
        in_shopping_cart = ShoppingCart.objects.filter(
            user=user,
            recipe=recipe
        )
        if in_shopping_cart:
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'not in shopping cart'},
            status=status.HTTP_400_BAD_REQUEST
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset модели Ingredient.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset модели Tag.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    '''Viewset модели User.'''
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    pagination_class = LimitPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action == 'list':
            self.permission_classes = [AllowAny]
        elif self.action == 'retrieve':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        '''Отображает текущего авторизованного пользователя.'''
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        '''Устанавливает новый пароль пользователю.'''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'],
        serializer_class=SubscriptionSerializer,
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

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
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
    def unsubscribe(self, request, pk=None):
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
