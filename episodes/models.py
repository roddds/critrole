import json
import datetime
from urllib.parse import urlencode
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

YOUTUBE_VIDEO_URL_PREFIX = "https://www.youtube.com/watch?"
YOUTUBE_EMBED_URL_PREFIX = "https://www.youtube.com/embed/"


class Episode(models.Model):
    video_id = models.TextField(verbose_name="Youtube identifier")
    chapter = models.IntegerField(verbose_name="Chapter number")
    title = models.TextField(verbose_name="Episode title")
    # running_time = models.DurationField(verbose_name="Episode running time")
    subtitle_filename = models.TextField(verbose_name="Episode subtitle file name")
    raw_captions = models.TextField(verbose_name="Raw caption contents")

    @property
    def watch_url(self):
        return YOUTUBE_VIDEO_URL_PREFIX + urlencode({"v": self.video_id})

    @property
    def embed_url(self):
        return YOUTUBE_EMBED_URL_PREFIX + self.video_id + "?"

    @property
    def full_text(self):
        return " ".join(self.captions.values_list("text", flat=True))

    def __str__(self):
        return f"{self.chapter} - {self.title}"


class CastMember(models.Model):
    name = models.TextField(verbose_name="Cast member name")

    def __str__(self):
        return f"{self.name}"


SECTIONS_FILE_PATH = "episodes/management/commands/sections.json"


class Caption(models.Model):
    episode = models.ForeignKey(
        "episodes.Episode", related_name="captions", on_delete=models.CASCADE
    )
    speakers = models.ManyToManyField("episodes.CastMember", related_name="lines")
    duration = models.DurationField(verbose_name="Line length in time")
    start = models.DurationField(verbose_name="Line start timestamp")
    end = models.DurationField(verbose_name="Line end timestamp")
    section = models.TextField(verbose_name="Section identifier", blank=True, null=True)
    text = models.TextField(verbose_name="Caption text")
    lines = ArrayField(models.TextField(name="line"))

    @property
    def previous(self):
        return (
            self.episode.captions.filter(start__lt=self.start)
            .order_by("-start")
            .first()
        )

    @property
    def next(self):
        return (
            self.episode.captions.filter(start__gt=self.start).order_by("start").first()
        )

    @property
    def url(self):
        return self.episode.embed_url + urlencode(
            {
                # Give it a small buffer so the playback
                # doesn't start or end too early
                "start": self.start.seconds - 1,
                "end": self.end.seconds + 2,
                "autoplay": "1",
            }
        )

    @property
    def start_ts(self):
        return self._to_timestamp(self.start)

    @property
    def end_ts(self):
        return self._to_timestamp(self.end)

    @staticmethod
    def _to_timestamp(duration):
        total_seconds = duration.total_seconds()
        hours = int(total_seconds / 3600)
        minutes = int(total_seconds / 60 - hours * 60)
        seconds = total_seconds - hours * 3600 - minutes * 60
        return "{:02d}:{:02d}:{:06.3f}".format(hours, minutes, seconds)

    @staticmethod
    def _from_timestamp(timestamp: str):
        hours, minutes, seconds = [float(x) for x in timestamp.split(":")]
        return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def __str__(self):
        return f"[{self.start_ts}-{self.end_ts}] {self.text[:30]}..."

    @staticmethod
    def apply_sections():
        with open(SECTIONS_FILE_PATH) as f:
            section_data = json.load(f)

        for episode_id, sections in section_data.items():
            episode = Episode.objects.get(id=episode_id)
            for section, timestamp in sections.items():
                if not timestamp:
                    continue
                episode.captions.filter(
                    start=Caption._from_timestamp(timestamp)
                ).update(section=section)

    def identify(self, section_type):
        """
        Section type can be:
            first_part
            break
            second_part
            ...more?
        """
        with open(SECTIONS_FILE_PATH) as f:
            sections = json.load(f)

        sections[str(self.episode.chapter)][section_type] = self.start_ts

        with open(SECTIONS_FILE_PATH, "w") as f:
            json.dump(sections, f, indent=2)
