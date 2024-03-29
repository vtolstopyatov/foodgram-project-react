from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    search_fields = ['username', 'email']


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(TokenProxy)
admin.site.unregister(Group)
