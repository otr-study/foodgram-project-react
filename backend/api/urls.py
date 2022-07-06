from django.urls import include, path
from rest_framework import routers

from .views import TagViewSet

router = routers.DefaultRouter()
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
