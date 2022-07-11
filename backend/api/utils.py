from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

def subscriptions_queryset(request):
    return User.objects.filter(
            subscriptions_author__subscriber=request.user
        ).prefetch_related(
            'recipes'
        ).annotate(recipes_count=Count('recipes__id'))
