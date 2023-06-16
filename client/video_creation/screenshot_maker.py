import json
import re
from pathlib import Path
import time
from typing import Dict ,Tuple, List

import translators as ts
# from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import ViewportSize, sync_playwright
from rich.progress import track

from utils import settings
from utils.console import print_step, print_substep
from utils.imagenarator import imagemaker




def get_screenshots_of_reddit_posts(reddit_object: dict, screenshot_num:List[int]):
    """
    Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """

    print_step("Downloading screenshots of reddit posts...")

    id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])

    # ! Make sure the reddit screenshots folder exists
    Path(f"assets/temp/{id}/png").mkdir(parents=True, exist_ok=True)

    # story=False
    theme = settings.config["settings"]["theme"]
    if theme == "dark":
        
        bgcolor = (*settings.config["image"]["dark_bg_color"], 0 if settings.config["image"]["bg_is_transparent"] else settings.config["image"]["bg_trans"]) 
        txtcolor = tuple(settings.config["image"]["dark_text_color"])
        cookie_file = open(
            "./video_creation/data/cookie-dark-mode.json", encoding="utf-8"
        )
    else:
        cookie_file = open("./video_creation/data/cookie-light-mode.json", encoding="utf-8")
        bgcolor = (255, 255, 255, 255)
        txtcolor = (0, 0, 0)

    if settings.config["settings"]["storymode"]  and settings.config["settings"]["storymodemethod"] == 1:
        
            # for idx,item in enumerate(reddit_object["thread_post"]):
            imagemaker(theme=bgcolor, reddit_obj=reddit_object, txtclr=txtcolor)

    if (
            not settings.config["settings"]["storymode"] 
            # or
            # settings.config["settings"]["storymodemethod"] == 0
        ):
        
        download(cookie_file, screenshot_num, reddit_object)
        


def download(cookie_file, num, reddit_object: dict) -> None:


    screenshot_num : List[int]  = num
    reddit_id = re.sub(r"[^\w\s-]", "", reddit_object["thread_id"])
    with sync_playwright() as p:
        print_substep("Launching Headless Browser...")
        # global browser
        browser = p.chromium.launch( headless=False)  #headless=True  #to see chrome
        W    : int = int(settings.config["settings"]["resolution_w"])
        H    : int = int(settings.config["settings"]["resolution_h"])
        lang : str = settings.config["reddit"]["thread"]["post_lang"]

        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        
        dsf = (W // 600) + 1
        context = browser.new_context(
            locale= lang or "en-us",
            device_scale_factor=dsf
            
        )

        cookies = json.load(cookie_file)

        context.add_cookies(cookies)  # load preference cookies
        # Get the thread screenshot
        page = context.new_page()
        page.goto(reddit_object["thread_url"], timeout=0)
        page.set_viewport_size(ViewportSize(width=settings.config["settings"]["vwidth"], height=H))


        if reddit_object["is_nsfw"] :

            page.locator("#AppRouter-main-content").get_by_role("button", name="Log In").click()
            page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_placeholder("\n        Username\n      ").fill(settings.config["reddit"]["creds"]["username"])
            page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_placeholder("\n        Password\n      ").fill(settings.config["reddit"]["creds"]["password"])
            page.wait_for_load_state()
            
            page.frame_locator("#SHORTCUT_FOCUSABLE_DIV iframe").get_by_role("button", name="Log In").click()
            page.locator('[data-test-id="post-content"]').screenshot(path="assets/temp/test/png/title1.png")



        if page.locator('[data-testid="content-gate"]').is_visible():

            # This means the post is NSFW and requires to click the proceed button.

            print_substep("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()
            page.wait_for_load_state()  # Wait for page to fully load

        if page.locator('[data-click-id="text"] button').is_visible(): 
            page.locator(
                '[data-click-id="text"] button'
            ).click()  # Remove "Click to see nsfw" Button in Screenshot

        ########################################################################################


        # if reddit_object["thread_post"] and  len(reddit_object["thread_post"]) > 600: 
        #     page.evaluate(
        #         "()=>document.querySelector(\"[data-test-id='post-content'] div.RichTextJSON-root\").textContent = '';"
        #         #   "[data-test-id='post-content'] div.RichTextJSON-root")
        #     )


        # TODO get the inner html with locator and inner html and put it back if have to take screenshot
        
        # translate code

        if settings.config["reddit"]["thread"]["post_lang"]:
            print_substep("Translating post...")
            texts_in_tl = ts.google( # type: ignore
                reddit_object["thread_title"],
                to_language=settings.config["reddit"]["thread"]["post_lang"],
            )

            page.evaluate(
                "tl_content => document.querySelector('[data-test-id=\"post-content\"] > div:nth-child(3) > div > "
                "div').textContent = tl_content",
                texts_in_tl,
            )
        if page.locator('[data-test-id="post-content"]').is_visible(): 
            page.locator('[data-test-id="post-content"]').screenshot(path=f"assets/temp/{reddit_id}/png/title.png")

        
        if page.locator(f'#t3_{reddit_id}').is_visible(): 
            page.locator(f'#t3_{reddit_id}').screenshot(path=f"assets/temp/{reddit_id}/png/title.png")

        if settings.config["settings"]["storymode"]: #TODO readd

            try:  # new change
                page.locator('[data-click-id="text"]').first.screenshot(
                    path=f"assets/temp/{reddit_id}/png/story_content.png"
                )
            except TimeoutError:
                exit()
        if settings.config["settings"]["allow_comment"]:
            for idx, comment in enumerate(
                    track(reddit_object["comments"], "Downloading screenshots...",reddit_object["comments"].__len__())
            ):
                # Stop if we have reached the screenshot_num
                if idx > screenshot_num[1]:
                    break

                if page.locator('[data-testid="content-gate"]').is_visible():
                    page.locator('[data-testid="content-gate"] button').click()
                page.goto(f'https://reddit.com{comment["comment_url"]}' , timeout=0)

                # translate code
                #document.querySelector("#t1_ji2hg0l > div.Comment.t1_ji2hg0l.P8SGAKMtRxNwlmLz1zdJu.HZ-cv9q391bm8s7qT54B3._1z5rdmX8TDr6mqwNv7A70U").style.width = "500px";
                if settings.config["reddit"]["thread"]["post_lang"]:
                    comment_tl = ts.google( # type: ignore
                        comment["comment_body"],
                        to_language=settings.config["reddit"]["thread"]["post_lang"],
                    )
                    page.evaluate(
                        '([tl_content, tl_id]) => document.querySelector(`#t1_${tl_id} > div:nth-child(2) > div > '
                        'div[data-testid="comment"] > div`).textContent = tl_content',
                        [comment_tl, comment["comment_id"]],
                    )
                try:
#################################################################################################################
                    page.locator(f"#t1_{comment['comment_id']}").screenshot(
                        path=f"assets/temp/{reddit_id}/png/comment_{idx}.png"
                    )
                except :# not work
                    # print("sddddddddddFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
                    del reddit_object["comments"][idx]
                    screenshot_num[1] -= 1
                    print("TimeoutError: Skipping screenshot...")
                    continue
                
        browser.close()

        # thread_post
        

    print_substep("Screenshots downloaded Successfully.", style="bold green")
