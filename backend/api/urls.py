from django.urls import include, path
from rest_framework import routers

from .views import (
    ExtendedUserViewSet, FavoriteViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, TagViewSet,
)

router = routers.DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shoping_cart'
)
router.register('users', ExtendedUserViewSet, 'users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
