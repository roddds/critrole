from episodes.views import CaptionViewSet, CastMemberViewSet, EpisodeViewSet
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'episode', EpisodeViewSet)
router.register(r'castmember', CastMemberViewSet)
router.register(r'caption', CaptionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
