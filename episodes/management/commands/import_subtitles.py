import os
import re
import datetime

from django.core.management.base import BaseCommand

from episodes.models import Episode, Caption, CastMember
import webvtt


TITLE_PATTERN = r"(?P<filename>^(?P<title>.+) _ Critical Role ?_ Campaign 2,? Episode (?P<chapter>\d+).*$)"
SPEAKER_PATTERN = r"(?P<speaker>^[A-Z]+):"
EMOTION_PATTERN = r"^[\(\[](?P<emotion>.+)[\)\]]$"


def parse_episode_subtitles(path):
    """
    "path" is a directory containing subtitles in VTT format
    for Campaign 2, downloaded with youtube-dl. Returns a list
    of dictionaries containing { title, filename, episode } (with
    `episode` being the episode number in the campaign), sorted
    by episode number.
    """
    filenames = [sub for sub in os.listdir(path) if sub.lower().endswith(".vtt")]
    parsed = [re.match(TITLE_PATTERN, fn).groupdict() for fn in filenames]
    return sorted(parsed, key=lambda x: int(x["chapter"]))


def get_episode_subtitles(filename):
    parser = webvtt.webvtt.WebVTT()
    return parser.read(filename).captions


class Command(BaseCommand):
    help = "Import subtitle directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "-p", "--path", type=str, help="Path to directory containing subtitles"
        )

    cast_member_cache = {}

    def get_cast_member(self, name):
        if cast_member := self.cast_member_cache.get(name):
            return cast_member

        self.cast_member_cache[name] = CastMember.objects.create(name=name)
        print(f"Added to cast: {name}")
        return self.cast_member_cache[name]

    def handle(self, path, *args, **kwargs):
        absolute_path = os.path.abspath(path)
        parsed_subtitles = parse_episode_subtitles(absolute_path)
        subtitle_parser = webvtt.WebVTT()

        for episode in parsed_subtitles:
            subtitle_abspath = os.path.join(absolute_path, episode["filename"])

            print(f'Creating Episode {episode["title"]}')
            with open(subtitle_abspath) as f:
                new_episode = Episode.objects.create(
                    chapter=episode["chapter"],
                    title=episode["title"],
                    subtitle_filename=episode["filename"],
                    raw_captions=f.read(),
                )

            episode_captions = subtitle_parser.read(subtitle_abspath).captions

            last_caption = None
            caption_instances = []

            for caption in episode_captions:
                speaker = re.match(SPEAKER_PATTERN, caption.text)

                if speaker is None:
                    is_emotion = bool(re.match(EMOTION_PATTERN, caption.text))
                    if is_emotion:
                        speaker_name = "All"
                    else:
                        last_caption._lines += caption.lines
                        last_caption._end = caption._end
                    continue
                else:
                    speaker_name = speaker["speaker"]
                    last_caption = caption

                caption_instances.append(
                    Caption(
                        episode=new_episode,
                        speaker=self.get_cast_member(speaker_name),
                        duration=datetime.timedelta(
                            seconds=caption._start - caption._end
                        ),
                        start=datetime.timedelta(seconds=caption._start),
                        end=datetime.timedelta(seconds=caption._end),
                    )
                )

            Caption.objects.bulk_create(caption_instances)
