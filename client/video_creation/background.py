import json
import os
import random
import re
import subprocess
import sys
from os import rename
from pathlib import Path
from random import randrange
from typing import Any, Tuple

from pytube import YouTube
from pytube.cli import on_progress

from utils import settings
from utils.console import print_step, print_substep
from utils.voice import getduration

# Load background videos
with open("utils/backgrounds.json") as json_file:
    background_options = json.load(json_file)

# Remove "__comment" from backgrounds
background_options.pop("__comment", None)

for name in list(background_options.keys()):
    pos = background_options[name][3]

    if pos != "center":
        background_options[name][3] = lambda t: ("center", pos + t)


def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000 * t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)

    cmd = [
        "ffmpeg", "-y", "-ss",
        "%0.2f" % t1, "-i", filename, "-t",
        "%0.2f" % (t2 - t1), "-map", "0", "-vcodec", "copy", "-acodec", "copy",
        "-loglevel", "warning", "-stats", targetname
    ]

    subprocess.run(cmd)


def get_start_and_end_times(video_length: float,
                            length_of_clip: float) -> Tuple[float, float]:
    """Generates a random interval of time to be used as the background of the video.

    Args:
        video_length (int): Length of the video
        length_of_clip (int): Length of the video to be used as the background

    Returns:
        tuple[int,int]: Start and end time of the randomized interval
    """
    random_time = randrange(180, int(length_of_clip) - int(video_length))
    return random_time, random_time + video_length


def get_background_config():
    """Fetch the background/s configuration"""
    try:
        choice = str(settings.config["settings"]["background"]
                     ["background_choice"]).casefold()
    except AttributeError:
        print_substep("No background selected. Picking random background'")
        choice = None

    # Handle default / not supported background using default option.
    # Default : pick random from supported background.
    if not choice or choice not in background_options:
        choice = random.choice(list(background_options.keys()))

    return background_options[choice]


def download_background(background_config: Tuple[str, str, str, Any]):
    """

    Downloads the background/s video from YouTube.
    
    """

    Path("./assets/backgrounds/").mkdir(parents=True, exist_ok=True)

    # note: make sure the file name doesn't include an - in it
    uri, filename, credit, _ = background_config
    bg_name = f'{credit}-{filename}'

    if Path(f"assets/backgrounds/{bg_name}").is_file():
        return

    print_step(
        "We need to download the backgrounds videos. they are fairly large but it's only done once. 😎"
    )
    Path("./assets/temp/").mkdir(parents=True, exist_ok=True)
    print_substep("Downloading the backgrounds videos... please be patient 🙏 ")

    print_substep(f"Downloading {filename} from {uri}")
    video = YouTube(uri, on_progress_callback=on_progress)
    video = video.streams.filter(res="1080p").first()
    if video is None:
        print("video not found")
        sys.exit()

    video.download("assets/temp", filename=f"{bg_name}")

    rename(
        f"assets/temp/{bg_name}",
        f"assets/backgrounds/{bg_name}",
    )

    print_substep("Background video downloaded successfully! 🎉",
                  style="bold green")


def chop_background_video(background_config: Tuple[str, str, str, Any],
                          video_length: float, reddit_object: dict):
    """Generates the background footage to be used in the video and writes it to assets/temp/background.mp4

    Args:
        background_config (Tuple[str, str, str, Any]) : Current background configuration
        video_length (int): Length of the clip where the background footage is to be taken out of
    """

    print_step("Finding a spot in the backgrounds video to chop...✂️")
    choice = f"{background_config[2]}-{background_config[1]}"
    id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    background_dur = getduration(f"assets/backgrounds/{choice}")

    start_time, end_time = get_start_and_end_times(video_length,
                                                   background_dur)

    ffmpeg_extract_subclip(
        f"assets/backgrounds/{choice}",
        start_time,
        end_time,
        targetname=f"assets/temp/{id}/background.mp4",
    )

    # in_clip = ffmpeg.input(f"assets/backgrounds/{choice}")
    # ffmpeg.trim(in_clip,start = start_time, end=end_time).output(f"assets/temp/{id}/background.mp4", **{
    #                                                                                                 "r":settings.config["settings"]["fps"] ,
    #                                                                                                  "c:v": "h264", "b:v": "4m", "b:a": "192k",
    #                                                                                                    "threads": multiprocessing.cpu_count(),
    #                                                                                                    "preset" :"ultrafast" if settings.config["settings"]["fast_render"] else "medium"
    #                                                                                                    }).overwrite_output().run()
    #TODO use ffmpeg-python instead of command
    return background_config[2]
