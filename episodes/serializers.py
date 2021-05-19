from rest_framework import serializers
from episodes.models import (
  Episode,
  CastMember,
  Caption,
)

class EpisodeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Episode
    fields = [
      'id',
      'video_id',
      'chapter',
      'title',
      'subtitle_filename',
    ]


class CastMemberSerializer(serializers.ModelSerializer):
  class Meta:
    model = CastMember
    fields = [
      'id',
      'name',
    ]


class CaptionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Caption
    fields = [
      'episode',
      'speakers',
      'duration',
      'start',
      'end',
      'text',
    ]
