from django.urls import include, path
from rest_framework import routers

from .views import (ExtendedUserViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/favorite',
    FavoriteViewSet
)
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/shopping_cart',
    ShoppingCartViewSet
)
router.register('users', ExtendedUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
