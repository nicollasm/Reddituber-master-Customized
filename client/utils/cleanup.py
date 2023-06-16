import os
import sys
from typing import List, NoReturn

from utils import settings
from utils.console import print_markdown


def _listdir(d) -> List[str]:  # listdir with full path
    return [os.path.join(d, f) for f in os.listdir(d)]


def cleanup(reddit_id) -> int:
    """Deletes all temporary assets in assets/temp

    Returns:
        int: How many files were deleted
    """
    if os.path.exists(f"{settings.cwd}/assets/temp/{reddit_id}/"):
        count = 0
        files = [f for f in os.listdir(f"{settings.cwd}/assets/temp/{reddit_id}/") if (f.endswith(".mp4") or f.endswith(".mp3") )]
        count += len(files)
        for f in files:
            os.remove(f"{settings.cwd}/assets/temp/{reddit_id}/{f}")
        REMOVE_DIRS = [f"{settings.cwd}/assets/temp/{reddit_id}/mp3/",f"{settings.cwd}/assets/temp/{reddit_id}/png/"]
        for d in REMOVE_DIRS:
            if os.path.exists(d):
                len_dir  = _listdir(d)
                count += len(len_dir)
                for f in len_dir:
                    os.remove(f)
                os.rmdir(d)
        os.rmdir(f"{settings.cwd}/assets/temp/{reddit_id}/")
        return count
    return 0


def shutdown(reddit_id= None) -> NoReturn:
    """
    Shutdown the bot and clear any temp
    """
    # try: 
    if reddit_id:
        if no_of_file:=cleanup(reddit_id) :
            print_markdown(f"## Cleared temp {no_of_file} files")

    # except:
        # pass
    print("Exiting...")
    sys.exit()