from django.urls import include, path
from rest_framework import routers

from api.views import (APISubscribtionCreateDelete, IngredientViewSet,
                       RecipeViewSet, SubscriptionViewSet, TagViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'users/subscriptions', SubscriptionViewSet,
                   basename='subscriptions')

urlpatterns = [
    path('users/<int:pk>/subscribe/', APISubscribtionCreateDelete.as_view(),
         name='api_subscribe'),
    path('', include(router_v1.urls)),
]
