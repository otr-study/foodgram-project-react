from django.urls import include, path
from rest_framework import routers

from .views import (ExtendUserViewSet, FavoriteViewSet, IngredientViewSet,
                    TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/favorite',
    FavoriteViewSet
)
router.register('users', ExtendUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
