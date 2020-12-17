from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import FavoriteViewSet, FollowViewSet

router_v1 = DefaultRouter(trailing_slash=False)
router_v1.register('favorites', FavoriteViewSet, basename='api_favorites')
router_v1.register('subscriptions', FollowViewSet, basename='api_follow')


urlpatterns = [
    path('', include(router_v1.urls)),
]
