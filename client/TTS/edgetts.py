import asyncio
import math
import os
import random
from typing import List

import edge_tts
from aiohttp import ClientConnectorError
from rich.progress import track

from utils import settings
from utils.voice import getduration

# edge-tts --rate=-50% --text "Hello, world!" --write-media hello_with_rate_halved.mp3

voices = (
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    "en-CA-ClaraNeural",
    "en-CA-LiamNeural",
    "en-HK-SamNeural",
    "en-HK-YanNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "en-IE-ConnorNeural",
    "en-IE-EmilyNeural",
    "en-KE-AsiliaNeural",
    "en-KE-ChilembaNeural",
    "en-NZ-MitchellNeural",
    "en-NZ-MollyNeural",
    "en-NG-AbeoNeural",
    "en-NG-EzinneNeural",
    "en-PH-JamesNeural",
    "en-PH-RosaNeural",
    "en-SG-LunaNeural",
    "en-SG-WayneNeural",
    "en-ZA-LeahNeural",
    "en-ZA-LukeNeural",
    "en-TZ-ElimuNeural",
    "en-TZ-ImaniNeural",
    "en-GB-LibbyNeural",
    "en-GB-MaisieNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
    "en-GB-ThomasNeural",
    "en-US-AriaNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural",
)


class edge:
    """
    Class for edge TTS 
    """

    def __init__(self) -> None:
        self.max_chars: int = 10**5
        self.voices = voices
        self.start_padding: float = 0
        self.startings: list[int] = []
        self.endings: list[int] = []
        # self.offsets:List[Tuple]    = []
        self.texts: List[str] = []
        self.has_sub = True

    def run(self, text, filepath, random_voice: bool = False) -> None:
        for _ in range(5):
            try:
                asyncio.new_event_loop().run_until_complete(
                    self._main(text, filepath, random_voice))
                break
            except ClientConnectorError:
                print("handling error")
                continue

    async def _main(self, text, filepath, random_voice: bool = False) -> None:

        if random_voice:
            voice = self.randomvoice()
        else:
            if not settings.config["settings"]["tts"]["edge_voice"]:
                raise ValueError(
                    f"Please set the config variable edge voice to a valid voice. options are: {voices}"
                )
        voice = settings.config["settings"]["tts"]["edge_voice"]

        speed = f'+{settings.config["settings"]["tts"]["edge_speed"]}%'
        communicate = edge_tts.Communicate(text, voice, rate=speed)
        startings: list[int] = []
        endings: list[int] = []
        texts = []
        with open(filepath, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # self.offsets.append((chunk["offset"],chunk["duration"]))
                    start = chunk["offset"] + (self.start_padding)
                    startings.append(start)
                    endings.append(start + chunk["duration"])
                    texts.append(chunk["text"])

        if settings.config["settings"]["storymodemethod"] == 0:
            self.make_ass(startings, endings, texts, filepath)

        self.update_last_time(filepath)

    def update_last_time(self, filename):
        """
        Update last time stamp so next time stamp will be after the prev
        
        """
        self.start_padding += getduration(filename) * 10**7
        #self.endings[-1].

    def make_ass(self, startings, endings, texts, name: str) -> None:
        """
        
        Makes the ASS file with current voice durtaion and text
        
        """
        file_data = ""
        file_data += '[Script Info]\n'
        file_data += 'Title: My Subtitle\n'
        file_data += 'ScriptType: v4.00+\n'
        file_data += f'PlayResX: {settings.config["settings"]["resolution_w"]}\n'
        file_data += f'PlayResY: {settings.config["settings"]["resolution_h"]}\n'
        file_data += '\n'
        file_data += '[V4+ Styles]\n'
        file_data += 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
        file_data += f'Style: Default,Carter One,{settings.config["fonts"]["single_word_font_size"]},     &Hffffff,       &H00000000,       &H00000000          ,&H0,        0,      0,     0,           0,      100,      100,      0,     0,      1,        3,        0,        10,      10,        10,     10,        1\n'
        file_data += '\n'
        file_data += '[Events]\n'
        file_data += 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'

        len_text = len(texts)
        for i in range(len_text):

            if not (i == 0 or i == (len_text - 1)):
                start_time = self.mktimestamp(startings[i])
                end_time = self.mktimestamp(startings[i + 1] - 10)
            else:
                start_time = self.mktimestamp(startings[i])
                end_time = self.mktimestamp(endings[i])

            file_data += f'Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,' + '{\\an5\\fscx90\\fscy90\\t(0,150,\\fscx100\\fscy100)}' + f'{texts[i].upper()}\n'

        with open(self.prepare_name(name) + ".ass", 'w',
                  encoding="utf-8") as f:
            f.write(file_data)

    def randomvoice(self) -> str:
        return random.choice(self.voices)

    @staticmethod
    def prepare_name(name: str) -> str:
        """
        Remove ``.mp3'`` at end of file name
        """

        if name.endswith(".mp3"):

            name, _ = os.path.splitext(name)
            return name
        raise

    @staticmethod
    def mktimestamp(time_unit: float) -> str:
        """
        mktimestamp returns the timecode of the subtitle.

        The timecode is in the format of 00:00:00.000.

        Returns:
            str: The timecode of the subtitle.
        """
        hour = math.floor(time_unit / 10**7 / 3600)
        minute = math.floor((time_unit / 10**7 / 60) % 60)
        seconds = (time_unit / 10**7) % 60
        return f"{hour:01d}:{minute:02d}:{seconds:06.2f}"
