from wsgiref.validate import validator

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import Count, OuterRef, Subquery
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.models import Favorite, IngredientRecipe, Recipe, ShoppingCart
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField,
                                        SlugRelatedField, ValidationError)
from rest_framework.validators import UniqueTogetherValidator
from tags.models import Tag
from users.models import Subscription

from .mixins import CommonSerializerMixin, QuerySerializerMixin

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


class CustomExtendedUserSerializer(QuerySerializerMixin, CustomUserSerializer):
    PREFETCH_FIELDS = ['recipes']
    
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
        queryset = User.objects.filter(
            subscriptions_author__author=instance.author,
            subscriptions_author__subscriber=request.user
        ).annotate(recipes_count=Count('recipes__id'))
        queryset = CustomExtendedUserSerializer.get_related_queries(queryset)
        context = {'request': request}
        return CustomExtendedUserSerializer(queryset[0], context=context).data


class IngredientRecipeReadSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(source='ingredient', read_only=True)
    name = SlugRelatedField(
        slug_field='name', source='ingredient', read_only=True
    )
    measurement_unit = SlugRelatedField(
        slug_field='measurement_unit', source='ingredient', read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagRecipeSerializer(ModelSerializer):
    tag = PrimaryKeyRelatedField(queryset=Tag.objects.all())
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    class Meta:
        model = Tag
        fields = ('tag', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('tag', 'recipe'),
                message='Дублирование записи.'
            )
        ]


class IngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    recipe = PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    amount = IntegerField(validators=(MinValueValidator(1),))
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'recipe', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('id', 'recipe'),
                message='Дублирование записи.'
            )
        ]


class RecipeInitialSerializer(QuerySerializerMixin, ModelSerializer):
    def get_initial_queryset(self, request):
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
        return self.get_related_queries(queryset)


class RecipeReadSerializer(RecipeInitialSerializer):
    PREFETCH_FIELDS = ['tags', 'ingredient_recipe']
    RELATED_FIELDS = ['author']

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeReadSerializer(
        many=True, source='ingredient_recipe'
    )
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)

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

    def get_is_favorited(self, obj):
        return obj.is_favorited is not None or False

    def get_is_in_shopping_cart(self, obj):
        return obj.is_in_shopping_cart is not None or False


class RecipeSerializer(RecipeInitialSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientRecipeSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        ingredients = map(
            lambda item: item.update({'recipe': recipe}),
            self.initial_data['ingredients']
        )

        # ingredients = [item.update({'recipe': recipe}) for item in ingredients]
        nested_ingredients_serializer = IngredientRecipeSerializer(
            data=ingredients, many=True
        )
        nested_ingredients_serializer.is_valid(raise_exception=True)
        nested_tags_serializer = self.fields['tags']
        nested_ingredients_serializer = self.fields['ingredients']
        nested_tags_serializer.create(tags)
        nested_ingredients_serializer.create(ingredients)

        # self.create_tags(tags, recipe)
        # self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ...

    def to_representation(self, instance):
        request = self.context['request']
        queryset = RecipeReadSerializer.get_initial_queryset(request).filter(
            id=instance.id
        )
        queryset = RecipeReadSerializer.get_related_queries(queryset)
        context = {'request': request}
        return RecipeReadSerializer(queryset[0], context=context).data
