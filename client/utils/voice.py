import re
import sys
import time as pytime
from datetime import datetime
from time import sleep
import ffmpeg

from requests import Response

# from utils import settings

if sys.version_info[0] >= 3:
    from datetime import timezone


def check_ratelimit(response: Response):
    """
    Checks if the response is a ratelimit response.
    If it is, it sleeps for the time specified in the response.
    """
    if response.status_code == 429:
        try:
            time = int(response.headers["X-RateLimit-Reset"])
            print(f"Ratelimit hit. Sleeping for {time - int(pytime.time())} seconds.")
            sleep_until(time)
            return False
        except KeyError:  # if the header is not present, we don't know how long to wait
            return False

    return True


def sleep_until(time):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """
    end = time

    # Convert datetime to unix timestamp and adjust for locality
    if isinstance(time, datetime):
        # If we're on Python 3 and the user specified a timezone, convert to UTC and get the timestamp.
        if sys.version_info[0] >= 3 and time.tzinfo:
            end = time.astimezone(timezone.utc).timestamp()
        else:
            zoneDiff = (
                pytime.time() - (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            )
            end = (time - datetime(1970, 1, 1)).total_seconds() + zoneDiff

    # Type check
    if not isinstance(end, (int, float)):
        raise Exception("The time parameter is not a number or datetime object")

    # Now we wait
    while True:
        now = pytime.time()
        diff = end - now

        #
        # Time is up!
        #
        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimize loop iterations
            sleep(diff / 2)

def getduration(filname) -> float:
    return float(ffmpeg.probe(filname)['format']['duration'])

def sanitize_text(text: str) -> str:
    r"""Sanitizes the text for tts.
        What gets removed:
     - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
     - any http or https links

    Args:
        text (str): Text to be sanitized

    Returns:
        str: Sanitized text
    """

    # remove any urls from the text
    regex_urls = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
    result = re.sub(regex_urls, " ", text)
    result = result.replace("+", "plus").replace("&", "and").replace("%","percent")
    acronyms = {
                "AITA" :"Am I The idiot?",
                "ESH": "Everyone Sucks Here",
                "NTA": "Not The idiot",
                "YTA": "You're The idiot",
                "NAH" :"No idoits Here",
                "INFO" :"Information",
                "SHP": "garbage post",
                "TLDR": "Too Long; Didn't Read?",
                "SJW": "Social Justice Warrior",
                "NTB" :"Not The Butt", 
                "WIBTA" : "would i be the idiot",
                "ETA" :"yes the idiot",
                'AFAIK': 'As Far As I Know',
                'AMA': 'Ask Me Anything',
                'AMITA': 'Am I The Asshole?',
                'ASAP': 'As Soon As Possible',
                'BFF': 'Best Friends Forever',
                'BRB': 'Be Right Back',
                'BTW': 'By The Way',
                'DAE': 'Does Anyone Else',
                'ELI5': "Explain Like I'm 5",
                'ETA': 'Edited To Add',
                'FTFY': 'Fixed That For You',
                'FWIW': "For What It's Worth",
                'FYI': 'For Your Information',
                'GG': 'Good Game',
                'GLHF': 'Good Luck, Have Fun',
                'HIFW': 'How I Feel When',
                'HTH': 'Hope That Helps',
                'IANAL': 'I Am Not A Lawyer',
                'IAmA': 'I Am A',
                'IDK': "I Don't Know",
                'IIRC': 'If I Remember Correctly',
                'IKR': 'I Know, Right?',
                'IMHO': 'In My Humble Opinion',
                'IMO': 'In My Opinion',
                'IRL': 'In Real Life',
                'ITT': 'In This Thread',
                'JK': 'Just Kidding',
                'LMAO': 'Laughing My back Off',
                'LMK': 'Let Me Know',
                'LOL': 'Laugh Out Loud',
                'MFW': 'My Face When',
                'MRW': 'My Reaction When',
                'NSFL': 'Not Safe For Life',
                'NSFW': 'Not Safe For Work',
                'OC': 'Original Content',
                'OP': 'Original Poster',
                'PM': 'Private Message',
                'PSA': 'Public Service Announcement',
                'ROFL': 'Rolling On The Floor Laughing',
                'SMH': 'Shaking My Head',
                'SO': 'Significant Other',
                'TIFU': 'Today got Into trouble  ',
                'TIL': 'Today I Learned',
                'TLDR': "Too Long; Didn't Read",
                'WTF': 'What The duck',
                'YMMV': 'Your Mileage May Vary',
                'YOLO': 'You Only Live Once' ,
                'gf' : 'girlfriend',
                'bf' : 'boyfriend'
                    }

    # change_able = acronyms.update(short_acronyms)  
    for acro , abr in acronyms.items():
        result = result.replace(acro,abr)
        result = result.replace("sexual"," intimate").replace("sex","ex").replace("WIBTA", "would i be the idiot").replace("fuck","duck").replace("dick","peepee").replace("ass","back")
        
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%—“”‘\"%\*/{}\[\]\(\)\\|<>=+]"# note: not removing apostrophes
    result = re.sub(regex_expr, " ", result)

    # pattern_mf = r'(\d+)\s*(m|f)'
    # result = re.sub(pattern_mf, r'\1 male' if '\2' == 'm' else r'\1 female', text) #covert male female not safe 



    result = " ".join(result.split())
    
    return result
