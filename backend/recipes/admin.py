from django.contrib import admin
from django.utils.html import format_html

from .models import Ingredient, IngredientAmount, Recipe, Tag


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    '''Админка ингредиентов'''
    list_display = ['name', 'id']
    ordering = ['name']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    '''Админка тегов.'''
    prepopulated_fields = {'slug': ['name']}
    readonly_fields = ['id']
    fields = ['id', 'name', 'slug', 'color']
    list_display = ['id', 'name', 'slug', 'now_color']

    @admin.display(description='Color')
    def now_color(self, instance):
        return format_html(
            '<span style="color: {};">{}</span>',
            instance.color,
            instance.color,
        )


class IngredientAmountInline(admin.TabularInline):
    '''Вспомогательный класс для ингредиентов в админке рецепта.'''
    model = IngredientAmount
    min_num = 1
    raw_id_fields = ['ingredients']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    '''Админка рецептов.'''
    readonly_fields = ['id']
    list_display = ['id', 'name', 'author']
    inlines = [IngredientAmountInline]
    search_fields = ['name', 'author__email']
    filter_horizontal = ['followers']
