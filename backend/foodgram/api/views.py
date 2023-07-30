from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeSerializerRead,
                             RecipeSerializerWrite, SubscribeSerializer,
                             SubscriptionSerializer, TagSerializer)
from api.utils import (create_favorite_cart, delete_favorite_cart,
                       generate_cart, get_author)
from recipes.models import (Cart, Favorite, Recipe, RecipeIngredient,
                            Subscription, Tag, User, Ingredient)
from djoser.views import UserViewSet as DjoserUserViewSet


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
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
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticated)

    def get_queryset(self):
        return User.objects.annotate(recipes_count=Count('recipes')).filter(
            following__subscriber=self.request.user.id)


class UserViewSet(DjoserUserViewSet):
    @action(methods=['POST', 'DELETE'],
            detail=False,
            url_path=r'(?P<pk>[^/.]+)/subscribe')
    def subscribe(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.create_subscribe(request)
        else:
            return self.delete_subscribe(request)

    def create_subscribe(self, request):
        author_id = get_author(request)
        data = {
            'subscriber': request.user.id,
            'author': author_id,
        }
        serializer = SubscribeSerializer(
            data=data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def delete_subscribe(self, request):
        author_id = get_author(request)
        subscribe = get_object_or_404(
            Subscription,
            subscriber_id=request.user.id,
            author_id=author_id
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
