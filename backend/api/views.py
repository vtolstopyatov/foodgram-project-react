from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from recipes.models import Recipes, Ingredients, Tags, Follow, ShoppingCart, IngredientsAmount
from .serializers import RecipesSerializer, UsersSerializer, IngredientsSerializer, TagsSerializer, FavoriteSerializer, SubscriptionsSerializer, ShoppingCartSerializer
from rest_framework import viewsets, mixins, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models.signals import m2m_changed
from django.core.signals import request_finished
from django.http import HttpResponse, FileResponse
from .filters import RecipesFilter
from io import BytesIO

User = get_user_model()


class LimitPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Добавляет рецепт в избранное"""
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
        """Удаляет рецепт из избранного"""
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
        """Возвращает файл списка покупок"""
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        recipes = []
        for i in shopping_cart:
            recipes.append(i.recipe)
        p = IngredientsAmount.objects.filter(recipe__in=recipes).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(Sum('amount'))
        to_file = ['Список покупок:\n'.encode("utf-8")]
        for i in p:
            name = i.get('ingredients__name')
            amount = i.get('amount__sum')
            measurment_unit = i.get('ingredients__measurement_unit')
            to_file.append(
                f'{name} — {amount} {measurment_unit}\n'.encode("utf-8")
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
        """Добавляет рецепт в список покупок"""
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
        """Удаляет рецепт из списка покупок"""
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


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        elif self.action == "list":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], serializer_class=SubscriptionsSerializer)
    def subscriptions(self, request, *args, **kwargs):
        """
        Возвращает пользователей, на которых подписан текущий пользователь.
        В выдачу добавляются рецепты
        """
        user = request.user
        pages = self.paginate_queryset(
            User.objects.filter(following__user=user).order_by('pk')
        )
        serializer = SubscriptionsSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
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
        serializer = SubscriptionsSerializer(author, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        user = request.user
        if user.follower.filter(user=user, author=author):
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'not subscribed'},
            status=status.HTTP_400_BAD_REQUEST
        )
