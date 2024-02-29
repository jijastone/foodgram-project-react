from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from colorfield.fields import ColorField
from foodgram.constants import (MAX_LENGTH, MIN_COOKING_TIME, MIN_AMOUNT,
                                MASSAGE_E_COOK, MAX_COOKING_TIME, MAX_AMOUNT,
                                MASSAGE_E_AMOUNT)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=MAX_LENGTH)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit'
        )]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH,
        unique=True)
    color = ColorField(
        'HEX код',
        default="#ffffff",
        unique=True)
    slug = models.SlugField(
        'Ссылка',
        max_length=MAX_LENGTH,
        unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор')
    name = models.CharField(
        'Название рецепта',
        max_length=MAX_LENGTH)
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='static/recipe/',
        blank=True,
        null=True)
    text = models.TextField(
        'Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(MIN_COOKING_TIME,
                                      message=MASSAGE_E_COOK),
                    MaxValueValidator(MAX_COOKING_TIME,
                                      message=MASSAGE_E_COOK)]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        related_name='recipeingredients',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт'

    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='',
        validators=[MinValueValidator(MIN_AMOUNT,
                                      message=MASSAGE_E_AMOUNT),
                    MaxValueValidator(MAX_AMOUNT,
                                      message=MASSAGE_E_AMOUNT)]
    )

    class Meta:
        verbose_name = 'Рецепт-ингредиент'
        verbose_name_plural = 'Рецепты-ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['ingredient', 'recipe'],
            name='unique_recipe_ingredient'
        )]

    def __str__(self):
        return f'{self.recipe} / {self.ingredient} / {self.amount}'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='in_favorites')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorites')]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='in_shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_shoppingcart')]
