from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, Recipe, RecipeIngredient, Tag)
from rest_framework.fields import (IntegerField, ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, ValidationError
from users.models import User
from users.serializers import CustomUserSerializer


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CreateIngredientSerializer(ModelSerializer):
    id = IntegerField(write_only=True)
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    cooking_time = IntegerField(min_value=1)
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def not_unique_items_validation(self, items):
        for item in items:
            if items.count(item) > 1:
                raise ValidationError(
                    'Нельзя добавить одни и те же ингридиенты')
        return items

    def validate_ingredient(self, items):
        for item in items:
            if not Ingredient.objects.filter(id=item['id']).exists():
                raise ValidationError('Не существует')
            if int(item['amount']) <= 0:
                raise ValidationError('мин кол-во ингридентов 1')

    def validate(self, data):

        tags = data.get('tags')
        if not tags:
            raise ValidationError('нет тэгов')
        self.not_unique_items_validation(tags)
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError('нет ингредиентов')
        self.validate_ingredient(ingredients)
        image = data.get('image')
        if not image:
            raise ValidationError('нет фотографии')
        self.not_unique_items_validation(ingredients)
        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.get('ingredients'), instance)
        instance.save()
        return instance

    def to_representation(self, recipe):
        return RecipeReadSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data


class IngredientAmountSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        read_only=True, source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = IntegerField(
        read_only=True, validators=(MinValueValidator(1),))

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientAmountSerializer(
        many=True, source='recipeingredients')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'name',
            'image',
            'text',
            'cooking_time',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False


class RecipeMiniSerializer(RecipeReadSerializer):
    class Meta():
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (*CustomUserSerializer.Meta.fields,
                  'recipes', 'recipes_count')
        read_only_fields = ("email", "username", "first_name", "last_name")

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        limit = int(self.context.get(
            "request").GET.get('recipes_limit', 10 ** 10))
        return RecipeMiniSerializer(
            Recipe.objects.filter(
                author=obj).all()[: limit], many=True, read_only=True
        ).data
