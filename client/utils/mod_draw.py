
import math
import textwrap

from PIL import Image
from PIL.ImageDraw import Image, ImageDraw

__all__ = ["Mod_ImageDraw"]
class Mod_ImageDraw(ImageDraw):


    def __init__(self, img) -> None:
        super().__init__(im=img)
        self.img : Image = img

    def fancy_Text(
        self,
        xy,
        text,
        output_name = "",
        output_suffix:int = 0,
        format="png" ,
        fill=None,
        font=None,
        anchor=None,
        spacing=4,
        align="left",
        direction=None,
        features=None,
        language=None,
        stroke_width=0,
        stroke_fill=None,
        embedded_color=False,
        save = False

    ) -> int:
        """
        Make multiline text 


        Returns 
        number of image generated
        """

        if isinstance(text,str) :
            uniq_char = tuple(set(text))
            avg_char_width = (sum(font.getsize(char)[0] for char in uniq_char) / len(uniq_char))
            max_char_count = math.ceil(self.img.size[0]   / avg_char_width)
            lines = textwrap.wrap(text,max_char_count)  # it is not 100% near the img width
            print(lines)
        else:
            lines = text


        if direction == "ttb":
            msg = "ttb direction is unsupported for multiline text"
            raise ValueError(msg)

        if anchor is None:
            anchor = "la"
        elif len(anchor) != 2:
            msg = "anchor must be a 2 character string"
            raise ValueError(msg)
        elif anchor[1] in "tb":
            msg = "anchor not supported for multiline text"
            raise ValueError(msg)

        


        widths = []
        max_width = 0
        # lines = self._multiline_split(text)
        line_spacing = self._multiline_spacing(font, spacing, stroke_width)
        for line in lines:
            line_width = self.textlength(
                line, font, direction=direction, features=features, language=language
            )
            widths.append(line_width)
            max_width = max(max_width, line_width)

        top = xy[1]
        if anchor[1] == "m":
            top -= (len(lines) - 1) * line_spacing / 2.0
        elif anchor[1] == "d":
            top -= (len(lines) - 1) * line_spacing

        for idx, line in enumerate(lines):
            left = xy[0]
            width_difference = max_width - widths[idx]

            # first align left by anchor
            if anchor[0] == "m":
                left -= width_difference / 2.0
            elif anchor[0] == "r":
                left -= width_difference

            # then align by align parameter
            if align == "left":
                pass
            elif align == "center":
                left += width_difference / 2.0
            elif align == "right":
                left += width_difference
            else:
                msg = 'align must be "left", "center" or "right"'
                raise ValueError(msg)

            self.text(
                (left, top),
                line,
                fill,
                font,
                anchor,
                direction=direction,
                features=features,
                language=language,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
                embedded_color=embedded_color,
            )
            if save:
                self.img.save(f"{output_name}{(output_suffix)}.{format}")   # not  working due to save not being in same class
            else:
                self.img.show(f"{output_name}{(output_suffix)}.{format}")
            top += line_spacing
            output_suffix+=1
        return output_suffix