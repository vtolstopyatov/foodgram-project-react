from django.contrib import admin
from .models import Recipes, Ingredients, IngredientsAmount, Tags
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets


admin.site.register(User, CustomUserAdmin)
admin.site.register(Recipes)
admin.site.register(Ingredients)
admin.site.register(IngredientsAmount)
admin.site.register(Tags)
