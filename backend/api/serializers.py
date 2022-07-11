from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from ingredients.models import Ingredient
from recipes.models import Favorite, Recipe
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        SerializerMethodField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator
from tags.models import Tag
from users.models import Subscription

from .utils import subscriptions_queryset

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


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)
        extra_kwargs = {
            'recipe': {'required': False},
            'user': {'required': False}
        }

    def validate(self, data):
        request = self.context['request']
        recipe = self.context['view'].kwargs['recipe_id']
        if Favorite.objects.filter(
            user=request.user, recipe__id=recipe
        ).exists():
            raise ValidationError('Дублирование записи.')
        return data

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeShortSerializer(instance.recipe, context=context).data


class RecipeShortSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class CustomExtendUserSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(many=True)
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

class SubscriptionSerializer(ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('__all__',)
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

    # def validate_author(self, value):
    #     if self.context.get('request').user == value:
    #         raise ValidationError(
    #             'Попытка подписаться на самого себя.'
    #         )
    #     return value

    def to_representation(self, instance):
        request = self.context['request']
        queryset = subscriptions_queryset(
            request
        ).filter(
            subscriptions_author__author=instance.author
        )
        context = {'request': request}
        return CustomExtendUserSerializer(queryset, context=context).data
