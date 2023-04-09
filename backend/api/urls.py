from django.urls import path, include
from rest_framework import routers
from .views import RecipesViewSet, UsersViewSet, IngredientsViewSet, TagsViewSet

v1_router = routers.DefaultRouter()


v1_router.register('recipes', RecipesViewSet, basename='recipes')
v1_router.register('ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register('tags', TagsViewSet, basename='tags')
# v1_router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
