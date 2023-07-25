from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializerRead,
                             RecipeSerializerWrite, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer)
from api.utils import (create_favorite_cart, delete_favorite_cart,
                       generate_cart, get_author)
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Subscription, Tag, User)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        ingredient_name = self.request.query_params.get('name')
        if ingredient_name:
            queryset = queryset.filter(
                Q(name__istartswith=ingredient_name) | Q(
                    name__icontains=ingredient_name))
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly]
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Recipe.custom_objects.add_user_annotations(
                self.request.user.id).all()
        return Recipe.custom_objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializerRead
        return RecipeSerializerWrite

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthorOrReadOnly, IsAuthenticated])
    def favorite(self, request, pk):
        return create_favorite_cart(FavoriteSerializer, request, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return delete_favorite_cart(Favorite, request, pk)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthorOrReadOnly, IsAuthenticated])
    def shopping_cart(self, request, pk):
        return create_favorite_cart(CartSerializer, request, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return delete_favorite_cart(Cart, request, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        queryset_ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit', ).order_by(
            'ingredient__name').annotate(total=Sum('amount'))

        return generate_cart(queryset_ingredients)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return User.objects.annotate(recipes_count=Count('recipes')).filter(
            following__subscriber=self.request.user.id)


class APISubscribtionCreateDelete(generics.CreateAPIView,
                                  generics.DestroyAPIView,
                                  generics.GenericAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthorOrReadOnly, IsAuthenticated]

    def perform_create(self, serializer):
        author_id = get_author(self.request)
        serializer.save(subscriber_id=self.request.user.id,
                        author_id=author_id)

    def destroy(self, request, *args, **kwargs):
        author_id = get_author(self.request)
        get_object_or_404(Subscription,
                          subscriber_id=self.request.user.id,
                          author_id=author_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
