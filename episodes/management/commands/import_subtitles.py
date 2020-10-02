import datetime
import os
import re

import humanfriendly
import webvtt
from django.core.management.base import BaseCommand
from episodes.models import Caption, CastMember, Episode

TITLE_PATTERN = r"(?P<filename>^(?P<title>.+) _ Critical Role ?_ Campaign 2,? Episode (?P<chapter>\d+).*?-(?P<video_id>[\w-]+)\.en\.vtt$)"
EMOTION_PATTERN = r"^[\(\[](?P<emotion>.+)[\)\]]$"

SPEAKERS_PATTERN = r"(?P<cast>([A-Z]+)((?:, *[A-Z]+)*),? *(and )*([A-Z]+)*):"


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


def split_subtitle(caption):
    """
    Most subtitles only contain lines from a single person. Sometimes
    they have more than two, like this:

    00:00:10.000 --> 00:00:12.000
    LIAM: Hi there.
    SAM: Hello.

    If that's the case, this splits them in two webvtt.Caption instances
    like this:

    00:00:10.000 --> 00:00:11.000
    LIAM: Hi there.

    00:00:11.000 --> 00:00:12.000
    SAM: Hello.
    """
    caption_length = len(caption.lines)

    if caption_length == 1:
        return [caption]

    if not re.match(SPEAKERS_PATTERN, caption.lines[1]):
        return [caption]

    half_time = (caption.end_in_seconds - caption.start_in_seconds) / 2

    first = webvtt.Caption(
        start=caption.start,
        end=caption._to_timestamp(caption.start_in_seconds + half_time),
        text=caption.lines[0],
    )

    second = webvtt.Caption(
        start=caption._to_timestamp(caption.start_in_seconds + half_time),
        end=caption.end,
        text=caption.lines[1],
    )

    return [first, second]


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
        name = name.strip()
        if cast_member := self.cast_member_cache.get(name):
            return cast_member

        self.cast_member_cache[name] = CastMember.objects.create(name=name)
        print(f"Added to cast: {name}")
        return self.cast_member_cache[name]

    def get_speakers(self, attribution_string):
        """
        examples:
            "MATT"
            "TALIESIN and MARISHA"
            "SAM, LAURA, and MATTHEW"
            "LIAM, LAURA, MATT, and ASHLEY"
            "LIAM, LAURA, MATT and ASHLEY"
        """
        return re.findall(
            r"[A-Z]+",
            attribution_string.replace(",", "")
            .replace(" and ", " ")
            .replace(" AND ", " "),
        )

    times_per_episode = []
    episode_count = 0
    start_time = datetime.datetime.now()

    def get_average_time(self):
        seconds_taken = sum([x.total_seconds() for x in self.times_per_episode])

        if len(self.times_per_episode) == 0:
            return datetime.timedelta()

        return datetime.timedelta(seconds=seconds_taken / len(self.times_per_episode))

    def get_time_until_done(self):
        # Average duration of episode parsing
        avg_time = self.get_average_time()
        # Predicted length of all parsing
        predicted_duration = datetime.timedelta(
            seconds=avg_time.total_seconds() * self.episode_count
        )
        predicted_ending = self.start_time + predicted_duration
        time_until_end = datetime.datetime.now() - predicted_ending

        return humanfriendly.format_timespan(abs(time_until_end), max_units=2)

    def handle(self, path, *args, **kwargs):
        absolute_path = os.path.abspath(path)
        parsed_subtitles = parse_episode_subtitles(absolute_path)
        subtitle_parser = webvtt.WebVTT()

        self.episode_count = len(parsed_subtitles)

        for episode in parsed_subtitles:
            start = datetime.datetime.now()
            subtitle_abspath = os.path.join(absolute_path, episode["filename"])

            print(
                f'[{self.get_time_until_done()}]\t Creating Episode {episode["chapter"]} - {episode["title"]}'
            )
            with open(subtitle_abspath) as f:
                new_episode = Episode.objects.create(
                    chapter=episode["chapter"],
                    video_id=episode["video_id"],
                    title=episode["title"].strip(),
                    subtitle_filename=episode["filename"],
                    raw_captions=f.read(),
                )

            episode_captions = subtitle_parser.read(subtitle_abspath).captions

            first_caption_in_speech = None
            joined_captions = []

            for original_caption in episode_captions:
                for vtt in split_subtitle(original_caption):
                    match = re.match(SPEAKERS_PATTERN, vtt.text)
                    speakers = match.groupdict().get("cast") if match else None

                    if speakers is None:
                        # This line is a continuation of a previous line,
                        # or a multiple-cast emotion, like "(laughs)"
                        is_emotion = bool(re.match(EMOTION_PATTERN, vtt.text))
                        if is_emotion:
                            speaker_names = ["ALL"]
                        else:
                            first_caption_in_speech._lines += vtt.lines
                            first_caption_in_speech._end = vtt._end
                        continue
                    else:
                        speaker_names = self.get_speakers(speakers)
                        first_caption_in_speech = vtt

                    vtt.speakers = speaker_names
                    joined_captions.append(vtt)

            instances = Caption.objects.bulk_create(
                [
                    Caption(
                        episode=new_episode,
                        text=" ".join(caption._lines),
                        lines=caption._lines,
                        duration=datetime.timedelta(
                            seconds=caption._start - caption._end
                        ),
                        start=datetime.timedelta(seconds=caption._start),
                        end=datetime.timedelta(seconds=caption._end),
                    )
                    for caption in joined_captions
                ]
            )

            line_assignments = []

            for vtt, instance in zip(joined_captions, instances):
                for person in vtt.speakers:
                    line_assignments.append(
                        Caption.speakers.through(
                            caption_id=instance.id,
                            castmember_id=self.get_cast_member(person).id,
                        )
                    )

            Caption.speakers.through.objects.bulk_create(line_assignments)

            end = datetime.datetime.now()

            self.times_per_episode.append(end - start)

        print(f"Total time: {datetime.datetime.now() - self.start_time}")
