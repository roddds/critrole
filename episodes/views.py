from rest_framework import viewsets
from episodes.models import (
  Episode,
  CastMember,
  Caption,
)
from episodes.serializers import (
  CaptionSerializer,
  CastMemberSerializer,
  EpisodeSerializer,
)

class EpisodeViewSet(viewsets.ModelViewSet):
  queryset = Episode.objects.all()
  serializer_class = EpisodeSerializer


class CastMemberViewSet(viewsets.ModelViewSet):
  queryset = CastMember.objects.all()
  serializer_class = CastMemberSerializer


class CaptionViewSet(viewsets.ModelViewSet):
  queryset = Caption.objects.all()
  serializer_class = CaptionSerializer
