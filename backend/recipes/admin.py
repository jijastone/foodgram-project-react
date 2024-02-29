from django.contrib import admin
from django.contrib.admin import display

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author', 'get_ingredients',
                    'get_tags', 'added_in_favorites')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (
        RecipeIngredientInline,
    )

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\t'.join(
            ingredient.name for ingredient in obj.ingredients.all()
        )

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return '\t'.join(
            tag.name for tag in obj.tags.all()
        )

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.in_favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(Favorite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)


@admin.register(RecipeIngredient)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
