from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import Count, OuterRef, Subquery
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.models import (Favorite, IngredientRecipe, Recipe, ShoppingCart,
                            TagRecipe)
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
    image = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.image.url


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
        model = TagRecipe
        fields = ('tag', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=TagRecipe.objects.all(),
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
    is_favorited = SerializerMethodField(read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    image = SerializerMethodField(read_only=True)

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
        return obj.is_favorited is not None or False

    def get_is_in_shopping_cart(self, obj):
        return obj.is_in_shopping_cart is not None or False

    @classmethod
    def get_queryset(cls, request):
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
        return cls.get_related_queries(queryset)


class RecipeSerializer(ModelSerializer):
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
        read_only_fields = ('author', 'tags', 'ingredients')

    def validate(self, data):
        self.validate_m2m_field(self.initial_data, 'ingredients')
        self.validate_m2m_field(self.initial_data, 'tags')
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
            item['id'] if type(item) == dict else item for item in data
        ]
        if len(values) != len(set(values)):
            raise ValidationError(
                f'Поле "{field_name}" должно содержить уникальные значения'
            )

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)

        self.validate_save_ingredients(self.initial_data, recipe)
        self.validate_save_tags(self.initial_data, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        self.validate_save_ingredients(
            self.initial_data, instance, is_update=True
        )
        self.validate_save_tags(self.initial_data, instance, is_update=True)

        return super().update(instance, validated_data)

    @staticmethod
    def validate_save_ingredients(initial_data, recipe, is_update=False):
        ingredients = initial_data['ingredients']
        [item.update({'recipe': recipe.id}) for item in ingredients]
        nested_ingredients_serializer = IngredientRecipeSerializer(
            data=ingredients, many=True
        )
        if is_update:
            IngredientRecipeSerializer.Meta.model.objects.filter(
                recipe=recipe.id
            ).delete()
        nested_ingredients_serializer.is_valid(raise_exception=True)
        nested_ingredients_serializer.save()

    @staticmethod
    def validate_save_tags(initial_data, recipe, is_update=False):
        tags = initial_data['tags']
        tags = [{'tag': item, 'recipe': recipe.id} for item in tags]
        nested_tags_serializer = TagRecipeSerializer(
            data=tags, many=True
        )
        if is_update:
            TagRecipeSerializer.Meta.model.objects.filter(
                recipe=recipe.id
            ).delete()
        nested_tags_serializer.is_valid(raise_exception=True)
        nested_tags_serializer.save()

    def to_representation(self, instance):
        request = self.context['request']
        queryset = RecipeReadSerializer.get_queryset(request).filter(
            id=instance.id
        )
        context = {'request': request}
        return RecipeReadSerializer(queryset[0], context=context).data

    def get_queryset(self, request):
        return Recipe.objects.all()
