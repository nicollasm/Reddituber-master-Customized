import base64
import random
import time

import requests
from requests.adapters import HTTPAdapter, Retry

from utils import settings

nonhuman = [  # DISNEY VOICES
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    # ENGLISH VOICES
]
human = [
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",
]
voices = nonhuman + human

noneng = [
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    # AMERICA VOICES
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # ASIA VOICES
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
]


# good_voices = {'good': ['en_us_002', 'en_us_006'],
#               'ok': ['en_au_002', 'en_uk_001']}  # less en_us_stormtrooper more less en_us_rocket en_us_ghostface


class TikTok:  # TikTok Text-to-Speech Wrapper
    def __init__(self) -> None:
        self.URI_BASE = "https://tiktok-tts.weilnet.workers.dev/api/generation"
        self.max_chars = 300
        self.voices = {"human": human, "nonhuman": nonhuman, "noneng": noneng}
        self.has_sub = False
        

    def run(self, text, filepath, random_voice: bool = False,retry=0):

        voice = settings.config["settings"]["tts"]["tiktok_voice"]

        payload = {
            "text": text,
            "voice": voice
        }
        headers = {
            "authority": "tiktok-tts.weilnet.workers.dev",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://weilbyte.github.io",
            "pragma": "no-cache",
            "referer": "https://weilbyte.github.io/",
            "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        }

        r = requests.request("POST", self.URI_BASE, json=payload, headers=headers)

        if not r.json()["success"]:
            if retry < 5:
                print()            
                time.sleep(3)
                self.run(text, filepath , retry=retry+1)
                raise ValueError(r.json()["error"],"In Tiktok TTS")

        vstr = r.json()["data"]
        b64d = base64.b64decode(vstr)

        with open(filepath, "wb") as out:
            out.write(b64d)
            
    def randomvoice(self) -> str:
        return random.choice(self.voices["human"])
