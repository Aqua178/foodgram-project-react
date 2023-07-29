from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.utils import get_author, check_ingredients
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
        request = self.context.get('request')
        if request:
            return obj.subscriber.filter(subscriber=request.user.id).exists()
        return False


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
    cooking_time = serializers.IntegerField(min_value=settings.MINVALUE,
                                            max_value=settings.MAXVALUE)

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, obj):
        return RecipeSerializerRead(obj).data

    def validate_ingredients(self):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ingredients': settings.MUST_HAVE_FIELD})
        ingredients = self.initial_data.pop('ingredients')
        all_ingredients = check_ingredients(ingredients)
        return all_ingredients

    def create_ingredients(self, ingredients, recipe):

        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
            ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = self.validate_ingredients()
        tags = validated_data.pop('tags')
        validated_data.setdefault(
            'author',
            self.context.get('request').user
        )
        recipe = super().create(validated_data)
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


class CartSerializer(serializers.ModelSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = Cart


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
