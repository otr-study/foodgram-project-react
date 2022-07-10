from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from tags.models import Tag

from api.serializers import (CustomExtendUserSerializer, FavoriteSerializer,
                             IngredientSerializer, TagSerializer)


class ExtendUserViewSet(UserViewSet):
    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset.select_related(
            'recipes'
        ).annotate(recipes_count=Count('recipes__id'))
        serializer = CustomExtendUserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class FavoriteViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    @action(detail=True, methods=['DELETE'])
    def delete(self, request, *args, **kwargs):
        favorite = Favorite.objects.filter(
            user=request.user,
            recipe__id=kwargs.get('recipe_id')
        )
        if not favorite.exists():
            return Response(
                data='Запись не существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
