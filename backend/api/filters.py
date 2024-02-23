from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    is_favorited = filters.CharFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.CharFilter(
        method='get_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    def get_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(in_favorites__user=self.request.user)
        return recipes

    def get_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(in_shopping_cart__user=self.request.user)
        return recipes

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
