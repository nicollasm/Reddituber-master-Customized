import multiprocessing
import os
import re
from os.path import exists
from typing import Any, Final, Tuple

import ffmpeg
from rich.console import Console
from rich.progress import track
from translators.server import google as google_ts

from utils import settings
from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.videos import save_data

console = Console()


def name_normalize(name: str) -> str:
    lang = settings.config["reddit"]["thread"]["post_lang"]
    if lang:
        print_substep("Translating filename...")

        name = google_ts(name, to_language=lang)  # type: ignore

    name = re.sub(r'[?\\"%*:|<>]', "", name[:100])
    name = re.sub(r"( [w,W]\s?\/\s?[o,O,0])", r" without", name)
    name = re.sub(r"( [w,W]\s?\/)", r" with", name)
    name = re.sub(r"(\d+)\s?\/\s?(\d+)", r"\1 of \2", name)
    name = re.sub(r"(\w+)\s?\/\s?(\w+)", r"\1 or \2", name)
    name = re.sub(r"\/", r"", name)
    name = re.sub(r"\n", r" ", name)

    return name


def put_images(background_clip, durations, number_of_clips,
               reddit_id):  # image_clips,
    """

    Utility to add text/image on background video

    """
    story_dur, comment_dur, title_dur = durations
    current_time = 0

    if (settings.config["settings"]["allow_title"]
            and settings.config["settings"]["storymodemethod"] != 0):
        if settings.config["settings"]["allow_title_picture"]:
            picture = ffmpeg.input(f"assets/temp/{reddit_id}/png/title.png")
            background_clip = background_clip.overlay(
                picture,
                enable=
                f"between(t,{current_time},{current_time + title_dur[0]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )

        current_time += title_dur[0]

    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 0:
            background_clip = ffmpeg.filter(
                background_clip,
                "subtitles",
                f"assets/temp/{reddit_id}/mp3/postaudio.ass",
                force_style="Alignment=10",
            )  # ,FontName='CarterOne-Regular.ttf',fontsdir='fonts'
            if settings.config["settings"]["allow_title_picture"]:
                background_clip = ffmpeg.filter(
                    background_clip,
                    "subtitles",
                    f"assets/temp/{reddit_id}/mp3/postaudio.ass",
                    force_style="Alignment=10",
                )  # ,FontName='CarterOne-Regular.ttf',fontsdir='fonts'
            current_time += story_dur[0]

        elif settings.config["settings"]["storymodemethod"] == 1:
            for i in track(range(number_of_clips[0]),
                           "Collecting the image files..."):
                picture = ff_input(f"assets/temp/{reddit_id}/png/img{i}.png")

                background_clip = background_clip.overlay(
                    picture,
                    enable=
                    f"between(t,{current_time},{current_time +  story_dur[i]})",
                    x="(main_w-overlay_w)/2",
                    y="(main_h-overlay_h)/2",
                )
                print(
                    f"between(t,{current_time},{current_time + story_dur[i]})")
                current_time += story_dur[i]

    if settings.config["settings"]["allow_comment"]:
        for i in range(number_of_clips[1]):
            picture = ff_input(f"assets/temp/{reddit_id}/png/comment_{i}.png")

            background_clip = background_clip.overlay(
                picture,
                enable=
                f"between(t,{current_time},{current_time +  comment_dur[i]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )
            current_time += comment_dur[i]

    return background_clip


def prepare_background(reddit_id: str, W: int, H: int) -> str:
    input_path = f"assets/temp/{reddit_id}/background.mp4"
    if settings.config["settings"]["crop"]:
        output_path = f"assets/temp/{reddit_id}/background_noaudio.mp4"
        output = (ffmpeg.input(input_path).filter(
                                        "crop", f"ih*({H}/{W})","ih")
                                        .filter("scale", f"{W}x{H}").output(
                output_path,
                an=None,
                **{
                    "c:v": "h264",
                    "b:v": "8M",
                    "threads": multiprocessing.cpu_count(),
                    "loglevel": "warning",
                    "stats": None,
                },
            ).overwrite_output())
        output.run()
        input_path = output_path

    return input_path


def ff_input(in_path, scr_width=1):
    return ffmpeg.input(in_path)


def make_final_video(
    number_of_clips: list[int],
    length: float,
    durations: list[list[float]],
    reddit_obj: dict,
    background_config: Tuple[str, str, str, Any],
):
    """Gathers audio clips, gathers all screenshots, stitches them together and saves the final video to assets/temp
    Args:
        number_of_clips (int): Index to end at when going through the screenshots'
        length (int): Length of the video
        durations (list[list[float]]) duration of title , posttext , comment
        reddit_obj (dict): The reddit object that contains the posts to read.
        background_config (Tuple[str, str, str, Any]): The background config to use.
    """
    # settings values
    W: Final[int] = int(settings.config["settings"]["resolution_w"])
    H: Final[int] = int(settings.config["settings"]["resolution_h"])
    allow_title = settings.config["settings"]["allow_title"]
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    # story_dur , comment_dur , title_dur = durations
    print_step("Creating the final video 🎥")
    background_clip = ffmpeg.input(prepare_background(reddit_id, W=W, H=H))

    # Gather all audio clips
    audio_clips = []
    if allow_title:
        audio_clips.append(
            ffmpeg.input(f"assets/temp/{reddit_id}/mp3/title.mp3"))

    if settings.config["settings"]["storymode"]:
        if settings.config["settings"]["storymodemethod"] == 0:
            audio_clips.append(
                ffmpeg.input(f"assets/temp/{reddit_id}/mp3/postaudio.mp3"))

        elif settings.config["settings"]["storymodemethod"] == 1:
            for i in track(range(number_of_clips[0]),
                           "Collecting the audio files..."):
                audio_clips.append(
                    ffmpeg.input(
                        f"assets/temp/{reddit_id}/mp3/postaudio-{i}.mp3"))

    if settings.config["settings"]["allow_comment"]:
        for i in track(range(number_of_clips[1]),
                       "Collecting the audio files..."):
            audio_clips.append(
                ffmpeg.input(f"assets/temp/{reddit_id}/mp3/{i}.mp3"))

    audio_concat = ffmpeg.concat(*audio_clips, a=1, v=0)
    ffmpeg.output(audio_concat, f"assets/temp/{reddit_id}/audio.mp3", **{
                                                                            "b:a": "192k",
                                                                            "loglevel": "warning",
                                                                            "stats": None,
                                                                        }).overwrite_output().run()

    console.print(f"[bold green] Video Will Be: {length:.2f} Seconds Long")
    # Gather all images
    # screenshot_width = int((W * 90) // 100)# FIXME (make sure this work correctly in all settings)

    audio = ffmpeg.input(f"assets/temp/{reddit_id}/audio.mp3")

    background_clip = put_images(background_clip, durations, number_of_clips,
                                 reddit_id)

    title = re.sub(r"[^\w\s-]", "", reddit_obj["thread_title"])

    filename = f"{name_normalize(title)[:251]}"
    subreddit = settings.config["reddit"]["thread"]["subreddit"]

    final = ffmpeg.output(
        background_clip,
        audio,
        f"results/{subreddit}/{filename}.mp4",
        f="mp4",
        **{
            "r":
            settings.config["settings"]["fps"],
            "c:v":
            "h264",
            "b:v":
            "4m",
            "b:a":
            "192k",
            "threads":
            multiprocessing.cpu_count(),
            "preset":
            "ultrafast"
            if settings.config["settings"]["fast_render"] else "medium",
            "loglevel":
            "warning",
            "stats":
            None,
        },
    ).overwrite_output()

    if not exists(f"./results/{subreddit}"):
        print_substep("The results folder didn't exist so I made it")
        os.makedirs(f"./results/{subreddit}")

    final.run()

    save_data(
        subreddit,
        filename + ".mp4",
        title,
        reddit_id,
        background_config[2],
    )
    print_step("Removing temporary files 🗑")

    # cleanups = cleanup(reddit_id)
    # print_substep(f"Removed {cleanups} temporary files 🗑")
    print_substep("See result in the results folder!")

    print_step(
        f'Reddit title: {reddit_obj["thread_title"]} \n Background Credit: {background_config[2]}'
    )
