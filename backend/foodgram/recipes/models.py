from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, UniqueConstraint

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.LENGTH200,
        verbose_name='Название продукта',
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=settings.LENGTH200,
        verbose_name='Еденица измерения',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_measurement_unit'
            ),
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.MODEL_STR_LIMIT]


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.LENGTH200,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=settings.LENGTH7,
        verbose_name='Цвет в HEX',
        blank=True,
        null=True,
        unique=True,
    )
    slug = models.SlugField(
        max_length=settings.LENGTH200,
        verbose_name='Слаг тега',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.MODEL_STR_LIMIT]


class RecipeQuerySet(models.QuerySet):

    def add_user_annotations(self, user_id):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
            is_in_shopping_cart=Exists(
                Cart.objects.filter(
                    user_id=user_id, recipe__pk=OuterRef('pk')
                )
            ),
        )


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=settings.LENGTH200,
        db_index=True,
        unique=True,
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(settings.MINVALUE)],
        db_index=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True, db_index=True)

    custom_objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('pub_date', 'name', 'author', 'cooking_time')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписавшийся пользователь')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецептов')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            UniqueConstraint(fields=('subscriber', 'author'),
                             name='Двойная подписка '),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('author')),
                name='Самоподписка')
        ]

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Продукт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(settings.MINVALUE)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'Ингредиент {self.ingredient} рецепта {self.recipe}'


class BaseUserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class Cart(BaseUserRecipe):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='cart_unique_recipe_user',

            ),
        ]
        default_related_name = 'carts'

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине {self.user}'


class Favorite(BaseUserRecipe):
    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='favorite_unique_recipe_user',

            ),
        ]
        default_related_name = 'favorites'

    def __str__(self):
        return f'Любимый рецепт {self.recipe} пользователя {self.user}'
