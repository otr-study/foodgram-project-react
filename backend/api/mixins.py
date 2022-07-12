from rest_framework.serializers import ValidationError


class CommonSerializerMixin:
    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return self.Meta.to_represent_serializer(
            instance.recipe, context=context
        ).data

    def validate(self, data):
        request = self.context['request']
        recipe = self.context['view'].kwargs['recipe_id']
        if self.Meta.model.objects.filter(
            user=request.user, recipe__id=recipe
        ).exists():
            raise ValidationError('Дублирование записи.')
        return data
