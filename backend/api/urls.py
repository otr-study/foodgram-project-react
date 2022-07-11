from django.urls import include, path
from rest_framework import routers

from .views import (ExtendedUserViewSet, FavoriteViewSet, IngredientViewSet,
                    TagViewSet)

router = routers.DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register(
    r'recipes/(?P<recipe_id>[\d]+)/favorite',
    FavoriteViewSet
)
router.register('users', ExtendedUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    # path('', include('djoser.urls')),
    path('', include(router.urls)),
]
