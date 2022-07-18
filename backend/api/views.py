import io

from django.contrib.auth import get_user_model
from django.db.models import Count, OuterRef, Subquery, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram_backend.settings import PDF_FONT

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnlyOrAdmin
from .serializers import (
    CustomExtendedUserSerializer, FavoriteSerializer, IngredientSerializer,
    RecipeReadSerializer, RecipeSerializer, ShoppingCartSerializer,
    SubscriptionSerializer, TagSerializer,
)
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, ShoppingCart
from tags.models import Tag
from users.models import Subscription

User = get_user_model()


class ExtendedUserViewSet(UserViewSet):
    @action(detail=False, methods=['GET'])
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(
            subscriptions_author__subscriber=request.user
        ).annotate(recipes_count=Count('recipes__id'))
        queryset = CustomExtendedUserSerializer.get_related_queries(queryset)

        context = {'request': request}
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CustomExtendedUserSerializer(
                page, many=True, context=context
            )
            return self.get_paginated_response(serializer.data)

        serializer = CustomExtendedUserSerializer(
            queryset, many=True, context=context
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, *args, **kwargs):
        data = {
            'subscriber': request.user.id,
            'author': kwargs.get('id')
        }
        context = {'request': request}
        serializer = SubscriptionSerializer(
            data=data, context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, *args, **kwargs):
        subscription = Subscription.objects.filter(
            subscriber=request.user,
            author=kwargs.get('id')
        )
        if not subscription.exists():
            return Response(
                data='Запись не существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class ShoppingCartViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        serializer.save(user=self.request.user, recipe=recipe)

    @action(detail=True, methods=['DELETE'])
    def delete(self, request, *args, **kwargs):
        shoping_cart = ShoppingCart.objects.filter(
            user=request.user,
            recipe__id=kwargs.get('recipe_id')
        )
        if not shoping_cart.exists():
            return Response(
                data='Запись не существует.',
                status=status.HTTP_400_BAD_REQUEST
            )
        shoping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnlyOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeSerializer

    def get_queryset(self):
        request = self.request
        serializer = self.get_serializer()
        query_is_favorited = Favorite.objects.filter(
            user=request.user.id,
            recipe=OuterRef('pk')
        )
        query_is_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user.id,
            recipe=OuterRef('pk')
        )
        queryset = Recipe.objects.all().annotate(
            is_favorited=Subquery(
                query_is_favorited.values('user')[:1]
            )
        ).annotate(
            is_in_shopping_cart=Subquery(
                query_is_in_shopping_cart.values('user')[:1]
            )
        )
        return serializer.get_related_queries(queryset)

    @action(
        detail=False, methods=['GET'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        font_object = TTFont('Arial', PDF_FONT)
        pdfmetrics.registerFont(font_object)
        pdf.setFont('Arial', size=16)

        shoping_cart = Ingredient.objects.filter(
            ingredient_recipe__recipe__shoping_cart__user=request.user
        ).annotate(
            amount=Sum('ingredient_recipe__amount')
        ).values_list('name', 'measurement_unit', 'amount')

        for i, (name, measurement_unit, amount) in enumerate(shoping_cart, 1):
            item = f'{i}. {name}: {amount}{measurement_unit}'
            pdf.drawString(50, 775 - i * 25, item)

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )
