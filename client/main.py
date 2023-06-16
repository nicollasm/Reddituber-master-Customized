#!/usr/bin/env python
import math
from os import name
from subprocess import Popen
import sys
from pathlib import Path
from typing import NoReturn

from prawcore import ResponseException

from reddit.subreddit import get_subreddit_threads
from utils import settings
from utils.cleanup import cleanup, shutdown
from utils.console import print_markdown, print_step
from utils.id import id
from video_creation.background import (chop_background_video,
                                       download_background,
                                       get_background_config)
from video_creation.final_video import make_final_video
from video_creation.screenshot_maker import get_screenshots_of_reddit_posts
from video_creation.voices import save_text_to_mp3

__VERSION__ = "2.6.0"


# ██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
# ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
# ██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
# ██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
# ██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
# ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝




def main(POST_ID=None) -> None:
    global reddit_object
    reddit_object = get_subreddit_threads(POST_ID)
    # redditid  = id(reddit_object)
    length, number_of_comments, audio_durations = save_text_to_mp3(reddit_object)
    # length = math.ceil(length)
    get_screenshots_of_reddit_posts(reddit_object, number_of_comments)
    bg_config = get_background_config()
    download_background(bg_config)
    chop_background_video(bg_config, length, reddit_object)
    make_final_video(number_of_comments, length,audio_durations, reddit_object, bg_config)


def run_many(times) -> None:
    for x in range(1, times + 1):
        print_step(
            f'on the {x}{("th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th")[x % 10]} iteration of {times}'
        )  # correct 1st 2nd 3rd 4th 5th....
        main()
        Popen("cls" if name == "nt" else "clear", shell=True).wait()


# def shutdown(reddit_id= None) -> NoReturn:
#     """
#     Shutdown the bot and clear any temp
#     """
#     # try: 
#     if reddit_id:
#         if no_of_file:=cleanup(reddit_id) :
#             print_markdown(f"## Cleared temp {no_of_file} files")

#     # except:
#         # pass
#     print("Exiting...")
#     sys.exit()


def run() -> None: 
    print(
    """
    ██████╗ ███████╗██████╗ ██████╗ ██╗████████╗    ██╗   ██╗██╗██████╗ ███████╗ ██████╗     ███╗   ███╗ █████╗ ██╗  ██╗███████╗██████╗
    ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝    ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗    ████╗ ████║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
    ██████╔╝█████╗  ██║  ██║██║  ██║██║   ██║       ██║   ██║██║██║  ██║█████╗  ██║   ██║    ██╔████╔██║███████║█████╔╝ █████╗  ██████╔╝
    ██╔══██╗██╔══╝  ██║  ██║██║  ██║██║   ██║       ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║    ██║╚██╔╝██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗
    ██║  ██║███████╗██████╔╝██████╔╝██║   ██║        ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝    ██║ ╚═╝ ██║██║  ██║██║  ██╗███████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝   ╚═╝         ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    )
    
    # print_markdown(
    #     "### Thanks for using this tool! [Feel free to contribute to this project on GitHub!](https://lewismenelaws.com) If you have any questions, feel free to reach out to me on Twitter or submit a GitHub issue. You can find solutions to many common problems in the [Documentation](): https://reddit-video-maker-bot.netlify.app/"
    # )
    # checkversion(__VERSION__)
    """
    main function to run bot

    """
    
    assert sys.version_info >= (3, 9), "Python 3.10 or higher is required"
    CWD = Path(__file__).parent.absolute()
    settings.cwd = CWD
    directory = Path().absolute()
    config = settings.check_toml(f"{directory}/utils/.config.template.toml", "config.toml")
    if not config :
        sys.exit()
    post_ids = config["reddit"]["thread"]["post_id"]
    try:
        if post_ids and  len(post_ids) != 1 :
            for index, post_id in enumerate(
                post_ids.split("+")
            ):
                index += 1
                print_step(
                    f'on the {index}{("th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th")[index % 10]} post of {len(post_ids.split("+"))}'
                )
                main(post_id)
                # Popen("cls" if name == "nt" else "clear", shell=True).wait()
        elif post_ids:
            print_step(f'Runing one time with {post_ids} !!')
            main(post_ids) 
        elif config["settings"]["times_to_run"]:
            run_many(config["settings"]["times_to_run"])
        else:
            main()
    except KeyboardInterrupt:
        shutdown(reddit_object.get("thread_post"))
    except ResponseException:
        # error for invalid credentials
        print_markdown("## Invalid credentials")
        print_markdown("Please check your credentials in the config.toml file")
        shutdown()
    except Exception as err:
        try :
            print_step(f'''Sorry, something went wrong with this test version! Try again, and feel free to report this issue at GitHub or the Discord community.'''
            f'''{__VERSION__}stm{str(config["settings"]["storymode"])} stmm {str(config["settings"]["storymodemethod"])} ptl {str(len(reddit_object["thread_post"]))}''')    
        except:
            print_step("something went wrong")
            raise err
        raise err
        # todo error

if __name__ == "__main__":
    run()