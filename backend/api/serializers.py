from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Ingredient, Recipe, RecipeIngredient,
                            Tag, Favorite, ShoppingCart)
from rest_framework.fields import (ReadOnlyField,
                                   SerializerMethodField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, ValidationError

from users.models import User, Subscription


class CustomUserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        return (user is not None
                and user.is_authenticated
                and user.subscriptions_as_user.filter(author=author).exists())


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class CreateIngredientSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                source='ingredient.id')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
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

    def not_unique_items_validation(self, items, message):
        s_items = set(items)
        if len(s_items) != len(items):
            raise ValidationError(
                f'Нельзя добавить одни и те же {message}')
        return items

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise ValidationError('нет тэгов')
        self.not_unique_items_validation(tags, 'теги')
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError('нет ингредиентов')
        image = data.get('image')
        if not image:
            raise ValidationError('нет фотографии')
        self.not_unique_items_validation(
            [ingredient['ingredient']['id'] for ingredient in ingredients],
            'ингридиенты')
        return data

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient['ingredient']['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipeReadSerializer(
            recipe,
            context={'request': self.context.get('request')},
        ).data


class IngredientAmountSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

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
        user = self.context.get('request').user
        return (user is not None
                and user.is_authenticated
                and user.favorites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user is not None
                and user.is_authenticated
                and user.shopping_cart.filter(recipe=obj).exists())


class RecipeMiniSerializer(RecipeReadSerializer):
    class Meta:
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
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        limit = self.context.get(
            'request').GET.get('recipes_limit')
        try:
            limit = int(limit)
        except ValueError:
            pass
        except TypeError:
            pass
        return RecipeMiniSerializer(
            Recipe.objects.filter(
                author=obj).all()[:limit], many=True, read_only=True
        ).data


class CreateFavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'recipe',
            'user'
        )

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Уже в избранном')
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMiniSerializer(
            instance.recipe, context={'request': request}
        ).data


class CreateShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = (
            'recipe',
            'user'
        )

    def validate(self, attrs):
        user = attrs['user']
        recipe = attrs['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Уже в покупках')
        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeMiniSerializer(
            instance.recipe, context={'request': request}
        ).data


class SubscriptionCreateSerializer(ModelSerializer):

    class Meta(CustomUserSerializer.Meta):
        model = Subscription
        fields = (
            'author',
            'user'
        )

    def to_representation(self, value):
        return SubscriptionSerializer(
            value.author,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        author = data['author']
        user = data['user']
        if author == user:
            raise ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Subscription.objects.filter(
                author=author,
                user=user).first():
            raise ValidationError(
                'Уже есть подписка'
            )
        return data
