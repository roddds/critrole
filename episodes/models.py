from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Episode(models.Model):
    chapter = models.IntegerField(verbose_name="Chapter number")
    title = models.TextField(verbose_name="Episode title")
    # url = models.TextField(verbose_name="Episode URL")
    # running_time = models.DurationField(verbose_name="Episode running time")
    subtitle_filename = models.TextField(verbose_name="Episode subtitle file name")
    raw_captions = models.TextField(verbose_name="Raw caption contents")

    def __str__(self):
        return f"{self.chapter} - {self.title}"


class CastMember(models.Model):
    name = models.TextField(verbose_name="Cast member name")

    def __str__(self):
        return f"{self.name}"


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

    text = models.TextField(verbose_name="Caption text")
    lines = ArrayField(models.TextField(name="line"))

    @property
    def start_ts(self):
        return self._to_timestamp(self.start)

    @property
    def end_ts(self):
        return self._to_timestamp(self.end)

    def _to_timestamp(self, duration):
        total_seconds = duration.total_seconds()
        hours = int(total_seconds / 3600)
        minutes = int(total_seconds / 60 - hours * 60)
        seconds = total_seconds - hours * 3600 - minutes * 60
        return "{:02d}:{:02d}:{:06.3f}".format(hours, minutes, seconds)

    def __str__(self):
        return f"[{self.start_ts}-{self.end_ts}] {self.text[:30]}..."
