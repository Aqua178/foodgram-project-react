from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscription, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 5
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeIngredientInline,
    ]
    list_display = (
        'id',
        'name',
        'author',
        'cooking_time',
        'get_ingredients',
        'get_tags',
        'favorites_count',
        'pub_date',
        'image_screen',
    )
    search_fields = ('name', 'author',)
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('favorites_count',)

    @admin.display(description='Счетчик избранных')
    def favorites_count(self, obj):
        return obj.favorites.all().count()

    @admin.display(description='Превью рецепта')
    def image_screen(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([str(tag) for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            [str(ingredient) for ingredient in obj.ingredients.all()])


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subscriber',
        'author'
    )
    search_fields = ('subscriber',)
    list_filter = ('author',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount',
    )
    list_editable = ('amount',)
    search_fields = ('recipe', 'ingredient',)
    list_filter = ('recipe', 'ingredient',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = ('user',)
    list_filter = ('user',)
