from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import Count
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField, ModelSerializer, PrimaryKeyRelatedField,
    SerializerMethodField, SlugRelatedField, ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from .mixins import CommonSerializerMixin, QuerySerializerMixin
from ingredients.models import Ingredient
from recipes.models import Favorite, IngredientRecipe, Recipe, ShoppingCart
from tags.models import Tag
from users.models import Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed')

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
    image = SerializerMethodField(read_only=True, method_name='get_image')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url


class FavoriteSerializer(CommonSerializerMixin, ModelSerializer):
    to_represent_serializer = RecipeShortSerializer

    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)
        read_only_fields = ('recipe', 'user')


class ShoppingCartSerializer(CommonSerializerMixin, ModelSerializer):
    to_represent_serializer = RecipeShortSerializer

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        read_only_fields = ('recipe', 'user')


class CustomExtendedUserSerializer(QuerySerializerMixin, CustomUserSerializer):
    PREFETCH_FIELDS = ['recipes']

    recipes = SerializerMethodField(read_only=True, method_name='get_recipes')
    recipes_count = IntegerField(read_only=True,)

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
        if attrs.get('author') == attrs.get('subscriber'):
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


class IngredientRecipeSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    amount = IntegerField(
        validators=(
            MinValueValidator(1, message='Значение не может быть меньше 1.'),)
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'recipe', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientRecipe.objects.all(),
                fields=('id', 'recipe'),
                message='Дублирование записи.'
            )
        ]


class RecipeReadSerializer(QuerySerializerMixin, ModelSerializer):
    PREFETCH_FIELDS = ['tags', 'ingredient_recipe']
    RELATED_FIELDS = ['author']

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeReadSerializer(
        many=True, source='ingredient_recipe'
    )
    is_favorited = SerializerMethodField(
        read_only=True, method_name='get_is_favorited'
    )
    is_in_shopping_cart = SerializerMethodField(
        read_only=True, method_name='get_is_in_shopping_cart'
    )
    image = SerializerMethodField(read_only=True, method_name='get_image')

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

    def get_image(self, obj):
        return obj.image.url

    def get_is_favorited(self, obj):
        request = self.context['request']
        return not request.user.is_anonymous and Favorite.objects.filter(
            recipe=obj, user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return not request.user.is_anonymous and ShoppingCart.objects.filter(
            recipe=obj, user=request.user
        ).exists()


class RecipeSerializer(QuerySerializerMixin, ModelSerializer):
    image = Base64ImageField()
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

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
        read_only_fields = ('author', 'tags', 'ingredients')

    def validate(self, data):
        ingredients = self.validate_m2m_field(
            self.initial_data, 'ingredients'
        )
        data['ingredients'] = self.validate_empty_field(ingredients, 'amount')
        data['tags'] = self.validate_m2m_field(self.initial_data, 'tags')
        return data

    @staticmethod
    def validate_m2m_field(collection, field_name):
        data = collection.get(field_name)
        if not data:
            raise ValidationError(
                f'Пропущенно обязательное поле "{field_name}"'
            )

        if not len(data):
            raise ValidationError(
                f'Поле "{field_name}" должно содержать не меньше 1 значения'
            )

        values = [
            item.get('id') if type(item) == dict else item for item in data
        ]
        if len(values) != len(set(values)):
            raise ValidationError(
                f'Поле "{field_name}" должно содержить уникальные значения'
            )
        return data

    @staticmethod
    def validate_empty_field(data, field_name):
        if len([value for value in data if not data[field_name]]):
            raise ValidationError(
                f'Пустое значение в поле "{field_name}"'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.validate_save_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.validate_save_ingredients(
            ingredients, instance, is_update=True
        )
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    @staticmethod
    def validate_save_ingredients(ingredients, recipe, is_update=False):
        for item in ingredients:
            item.update({'recipe': recipe.id})

        nested_ingredients_serializer = IngredientRecipeSerializer(
            data=ingredients, many=True
        )
        if is_update:
            IngredientRecipeSerializer.Meta.model.objects.filter(
                recipe=recipe.id
            ).delete()
        nested_ingredients_serializer.is_valid(raise_exception=True)
        nested_ingredients_serializer.save()

    def to_representation(self, instance):
        request = self.context['request']
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data
