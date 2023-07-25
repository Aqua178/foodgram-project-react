from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import get_author
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscription, Tag)
from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request', False)
        return (request and request.user.is_authenticated
                and Subscription.objects.filter(
                    author=obj,
                    subscriber=request.user.id).exists())


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializerRead(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    tags = TagSerializer(many=True, )
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(many=True, read_only=True,
                                             source='recipeingredients')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        read_only_fields = ('id', 'author',)


class RecipeSerializerWrite(serializers.ModelSerializer):
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=settings.MINVALUE)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, obj):
        return RecipeSerializerRead(obj).data

    def validate_tags(self, value):
        tags = self.initial_data.pop('tags')
        tags_ids = []
        for tag in tags:
            if not (isinstance(tag, int) and tag > 0):
                raise serializers.ValidationError(
                    {'tags': settings.NOT_POSITIVE_INTEGER_TAG.format(
                        tag=tag)})
            tags_ids.append(tag)
            if len(tags_ids) != len(set(tags_ids)):
                raise serializers.ValidationError(
                    {'tags': settings.DUPLICATE_TAGS.format(
                        tag=tag)})
        return value

    def validate_ingredients(self):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': settings.MUST_HAVE_FIELD})
        ingredients = self.initial_data.pop('ingredients')
        if not (isinstance(ingredients, list)
                and len(ingredients) > 0):
            raise serializers.ValidationError(
                {'ingredients': settings.NOT_LIST_INGREDIENT.format(
                    ingredients=ingredients)})
        ingredient_ids = []
        for ingredient in ingredients:
            if 'amount' not in ingredient:
                raise serializers.ValidationError(
                    {'amount': settings.MUST_HAVE_FIELD_AMOUNT.format(
                        ingredient=ingredient)})
            if 'id' not in ingredient:
                raise serializers.ValidationError(
                    {'id': settings.MUST_HAVE_FIELD_ID.format(
                        ingredient=ingredient)})
            try:
                int(ingredient['amount'])
                if not int(ingredient['amount']) > 0:
                    raise serializers.ValidationError(
                        {'amount': settings.NOT_POSITIVE_INTEGER.format(
                            ingredient=ingredient)})
            except ValueError:
                raise serializers.ValidationError(
                    {'amount': settings.NOT_POSITIVE_INTEGER.format(
                        ingredient=ingredient)})
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    {'ingredients': settings.NO_INGREDIENT.format(
                        ingredient=ingredient)})
            ingredient_ids.append(ingredient['id'])
            if len(ingredient_ids) != len(set(ingredient_ids)):
                raise serializers.ValidationError(
                    {'ingredients': settings.DUPLICATE_INGREDIENTS.format(
                        ingredient=ingredient)})
        return ingredients

    def create_ingredients(self, ingredients, recipe):

        obj = [RecipeIngredient(recipe=recipe,
                                ingredient_id=ingredient['id'],
                                amount=ingredient['amount'])
               for ingredient in ingredients]
        obj.sort(key=(lambda item: item.ingredient.name), reverse=True)
        RecipeIngredient.objects.bulk_create(obj)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = self.validate_ingredients()
        tags = validated_data.pop('tags')
        recipe = Recipe.custom_objects.create(**validated_data,
                                              author_id=self.context.get(
                                                  'request').user.id)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = self.validate_ingredients()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance, ).delete()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)


class ShortRecipe(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user', 'recipe',)

    def to_representation(self, obj):
        return ShortRecipe(obj.recipe, context={
            'request': self.context.get('request')}).data

    def validate(self, attrs):
        if (self.context.get('request').method == 'POST'
                and Favorite.objects.filter(
                    recipe_id=self.context.get('pk'),
                    user_id=self.context.get('request').user.id).exists()):
            raise serializers.ValidationError(
                {settings.DUPLICATE_FAVORITES.format(
                    recipe=self.context.get('pk'))})
        return attrs


class CartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Cart

    def validate(self, attrs):
        if (self.context.get('request').method == 'POST'
                and Cart.objects.filter(
                    recipe_id=self.context.get('pk'),
                    user_id=self.context.get('request').user.id).exists()):
            raise serializers.ValidationError(
                {settings.RECIPE_ALREADY_IN_CART.format(
                    recipe=self.context.get('pk'))})
        return attrs


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('subscriber', 'author',)

    def to_representation(self, obj):
        return SubscriptionSerializer(obj.author, context={
            'request': self.context.get('request')}).data

    def validate(self, attrs):
        author_id = get_author(self.context.get('request'))
        subscriber = self.context.get('request').user
        author = get_object_or_404(User, pk=author_id)
        subscription = Subscription.objects.filter(author=author,
                                                   subscriber=subscriber)
        if author == subscriber:
            raise serializers.ValidationError(
                {settings.SELF_SUBSCRIPTION.format(
                    author=author, subscriber=subscriber)})
        if self.context.get('request').method == 'POST':
            if subscription.exists():
                raise serializers.ValidationError(
                    {settings.DUPLICATE_SUBSCRIPTION.format(
                        author=author)})
        return attrs


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count',)

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit')
        user_recipes = obj.recipes.all()
        if recipes_limit:
            user_recipes = user_recipes[:int(recipes_limit)]
        return ShortRecipe(user_recipes, many=True, context={
            'request': self.context.get('request')}).data
