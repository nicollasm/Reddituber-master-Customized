import re
import textwrap

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track

from TTS.engine_wrapper import process_text
from utils import settings


def smart_MText(
    text: str,
    max_w: int,
    font,  #
    path ,
    txt_clr="white",
    bg_clr="black",
    line_spacing=10,
    padding_block: int = 0,
    padding_inline: int = 0,
    align="c",
    *args,
    **kwargs,
):
    uniq_char = list(set(text))
    avg_font_w = sum(font.getsize(char)[0] for char in uniq_char) / len(uniq_char)

    max_char_count = int((max_w + padding_inline) / (avg_font_w))
    texts = textwrap.wrap(text, max_char_count)
    text_wh = (font.getsize(s) for s in texts)
    w, h = map(list, zip(*text_wh))

    im_w = min(max_w, max(w)) + (padding_inline * 2)
    im_h = (
        sum(h) + (line_spacing * max(len(h) - 1, 0)) + (padding_block * 2)
    )  # 7 for stroke offset top bottom

    im = Image.new("RGBA", (im_w, im_h), bg_clr)
    canvas = ImageDraw.Draw(im)
    y = padding_block

    for i, t in enumerate(texts):
        if align == "c":
            x = (im_w - w[i]) / 2
        elif align == "l":
            x = padding_inline
        elif align == "r":
            x = im_w - w[i]
        else:
            raise ValueError("Wrong algin type must be 'r' , 'l' or 'c' ")
        canvas.multiline_text
        canvas.text(
            (x, y),
            t.strip(),
            txt_clr,
            font,
            stroke_width=3,
            stroke_fill="black",  # TODO
        )

        y += line_spacing + h[i]
    im.save(path)


def imagemaker(theme, reddit_obj: dict, txtclr) -> None:
    """
    Render Images for video
    """

    reddit_id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])
    font = ImageFont.truetype(
        f"fonts/{settings.config['fonts']['normal_font']}", settings.config["fonts"]["normal_font_size"]
    )

    if settings.config["settings"]["allow_title"]:
        title = reddit_obj["thread_title"]
        tfont = ImageFont.truetype(
            f"fonts/{settings.config['fonts']['title_font']}", settings.config["fonts"]["title_font_size"] 
        )

        smart_MText(
            text=process_text(title),
            max_w=settings.config["image"]["max_im_w_story"],
            font=tfont,
            path=f"assets/temp/{reddit_id}/png/title.png",
            txt_clr=txtclr,
            bg_clr=theme,
        )
        del tfont
    if settings.config["settings"]["storymode"]:
        posttext = reddit_obj["thread_post"]

        if isinstance(posttext, str):
            raise TypeError("style 2 require list or tuple containing str not str")

        for idx, text in track(enumerate(posttext), "Making post image..."):
            smart_MText(
                text=process_text(text),
                max_w=settings.config["image"]["max_im_w_story"],
                font=font,
                path=f"assets/temp/{reddit_id}/png/img{idx}.png",
                txt_clr=txtclr,
                bg_clr=theme,
            )

    if settings.config["settings"]["allow_comment"]:
        comments = reddit_obj["comments"]

        for idx, text in track(enumerate(comments["comment_body"]), "Making Comment Image..."):
            smart_MText(
                text=process_text(text),
                max_w=settings.config["image"]["max_im_w_story"],
                font=font,
                path=f"assets/temp/{reddit_id}/png/comment_{idx}.png",
                txt_clr=txtclr,
                bg_clr=theme,
            )
