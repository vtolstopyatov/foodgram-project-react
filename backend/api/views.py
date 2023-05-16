from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from recipes.models import Recipes, Ingredients, Tags
from .serializers import RecipesSerializer, UsersSerializer, IngredientsSerializer, TagsSerializer, FavoriteSerializer
from rest_framework import viewsets, mixins, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models.signals import m2m_changed
from django.core.signals import request_finished
from .filters import RecipesFilter

User = get_user_model()


class LimitPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags__slug',)
    filterset_class = RecipesFilter



    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
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
    def delete_password(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if recipe.followers.filter(pk=user.pk):
            recipe.followers.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'not in favorites'},
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
        return self.retrieve(request, *args, **kwargs)