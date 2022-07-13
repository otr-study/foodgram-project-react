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


class QuerySerializerMixin:
    PREFETCH_FIELDS = []
    RELATED_FIELDS = []

    @classmethod
    def get_related_queries(cls, queryset):
        if cls.RELATED_FIELDS:
            queryset = queryset.select_related(*cls.RELATED_FIELDS)
        if cls.PREFETCH_FIELDS:
            queryset = queryset.prefetch_related(*cls.PREFETCH_FIELDS)
        return queryset
