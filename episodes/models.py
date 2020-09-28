from django.db import models

# Create your models here.


class Episode(models.Model):
    chapter = models.IntegerField(verbose_name="Chapter number")
    title = models.TextField(verbose_name="Episode title")
    # url = models.TextField(verbose_name="Episode URL")
    # running_time = models.DurationField(verbose_name="Episode running time")
    subtitle_filename = models.TextField(verbose_name="Episode subtitle file name")
    raw_captions = models.TextField(verbose_name="Raw caption contents")


class CastMember(models.Model):
    name = models.TextField(verbose_name="Cast member name")


class Caption(models.Model):
    episode = models.ForeignKey(
        "episodes.Episode", related_name="captions", on_delete=models.CASCADE
    )
    speaker = models.ForeignKey(
        "episodes.CastMember", related_name="lines", on_delete=models.CASCADE
    )
    duration = models.DurationField(verbose_name="Line length in time")
    start = models.DurationField(verbose_name="Line start timestamp")
    end = models.DurationField(verbose_name="Line end timestamp")
