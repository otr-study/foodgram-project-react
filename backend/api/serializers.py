from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe, ShoppingCart
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator
from tags.models import Tag
from users.models import Subscription

from .mixins import CommonSerializerMixin

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return not request.user.is_anonymous and Subscription.objects.filter(
            author=obj, subscriber=request.user
        ).exists()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(CommonSerializerMixin, ModelSerializer):
    class Meta:
        to_represent_serializer = RecipeShortSerializer
        model = Favorite
        fields = ('recipe', 'user',)
        extra_kwargs = {
            'recipe': {'required': False},
            'user': {'required': False}
        }


class ShoppingCartSerializer(CommonSerializerMixin, ModelSerializer):
    class Meta:
        to_represent_serializer = RecipeShortSerializer
        model = ShoppingCart
        fields = ('recipe', 'user')
        extra_kwargs = {
            'recipe': {'required': False},
            'user': {'required': False}
        }


class CustomExtendedUserSerializer(CustomUserSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes_count',
            'recipes',
        )

    @classmethod
    def get_queryset(cls, request):
        return User.objects.filter(
            subscriptions_author__subscriber=request.user
        ).prefetch_related(
            'recipes'
        ).annotate(recipes_count=Count('recipes__id'))

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = recipes_limit and recipes[:int(recipes_limit)] or recipes
        return RecipeShortSerializer(recipes, many=True).data


class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'subscriber')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author', 'subscriber'),
                message='Дублирование записи.'
            )
        ]

    def validate(self, attrs):
        if attrs['author'] == attrs['subscriber']:
            raise ValidationError(
                'Попытка подписаться на самого себя.'
            )
        return attrs

    def to_representation(self, instance):
        request = self.context['request']
        queryset = CustomExtendedUserSerializer.get_queryset(request)
        queryset.filter(
            subscriptions_author__author=instance.author
        )
        context = {'request': request}
        return CustomExtendedUserSerializer(queryset[0], context=context).data


class RecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
