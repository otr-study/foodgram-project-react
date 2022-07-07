from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from ingredients.models import Ingredient
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from tags.models import Tag
from users.models import Subscription

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
