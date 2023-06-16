from pathlib import Path
from typing import NoReturn
import requests
import os
import subprocess
from rich.progress import track
from utils.console import  print_substep
from utils.cleanup import shutdown
from utils import settings

def ffmpeg_install_windows() -> NoReturn:

    if not os.path.exists(settings.cwd.joinpath("ffmpeg/ffmpeg.exe")):
        print("ffmpeg is not downloaded ")

        try:
            zip = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            with requests.get(zip, stream=True)as r:
                with open("ffmpeg.zip", "wb") as f:
                    for chunk in track(r.iter_content(chunk_size=8192)): 
                        f.write(chunk)

            import zipfile

            with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
                zip_ref.extractall()

            os.remove("ffmpeg.zip")
            os.rename("ffmpeg-master-latest-win64-gpl", "ffmpeg")

            # Move the files inside bin to the root
            for file in os.listdir("ffmpeg/bin"):
                os.rename(f"ffmpeg/bin/{file}", f"ffmpeg/{file}")
            os.rmdir("ffmpeg/bin")

            for file in os.listdir("ffmpeg/doc"):
                os.remove(f"ffmpeg/doc/{file}")
            os.rmdir("ffmpeg/doc")

        except ConnectionError as e:
            print("network error occured")
            raise e
        
        except Exception as e:
            print(
                "An error occurred while trying to install FFmpeg. Please try again. Otherwise, please install FFmpeg manually and try again.")
            print(e)
            shutdown()

        
    import winreg

    new_path = str(settings.cwd.joinpath("ffmpeg")
)
    # get the current PATH variable
    path = os.environ['PATH']

    # append the new directory to the PATH variable
    os.environ['PATH'] = new_path + ';' + path

    # set the new PATH value in the registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, os.environ['PATH'])
            print_substep("Added Path to system Now FFmpeg should work","green")
    except PermissionError as e:
        print_substep("Please run Bot as administrator","bold red")
        raise e
    

    print_substep("FFmpeg installed successfully! Please restart your computer and then re-run the program.","green")
    shutdown()


def ffmpeg_install_linux() -> NoReturn:
    try:
        subprocess.run("sudo apt install ffmpeg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(
            "An error occurred while trying to install FFmpeg. Please try again. Otherwise, please install FFmpeg manually and try again.")
        print(e)
        shutdown()
    print("FFmpeg installed successfully! Please re-run the program.")
    shutdown()


def ffmpeg_install_mac() -> NoReturn:
    try:
        subprocess.run("brew install ffmpeg", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(
            "Homebrew is not installed. Please install it and try again. Otherwise, please install FFmpeg manually and try again.")
        shutdown()
    print("FFmpeg installed successfully! Please re-run the program.")
    shutdown()


def ffmpeg_install() -> None:
    try:
        # Try to run the FFmpeg command
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(settings.cwd.joinpath("results/")):
            print('FFmpeg is installed on this system! If you are seeing this error for the second time, restart your computer.',"")
    except FileNotFoundError as e:
        print('FFmpeg is not installed on this system.')
        resp = input("We can try to automatically install it for you. Would you like to do that? (y/n): ")
        if resp.lower() == "y":
            print("Installing FFmpeg...")
            if os.name == "nt":
                ffmpeg_install_windows()
            elif os.name == "posix":
                ffmpeg_install_linux()
            elif os.name == "mac":
                ffmpeg_install_mac()
            else:
                print("Your OS is not supported. Please install FFmpeg manually and try again.")
                exit()
        else:
            print("Please install FFmpeg manually and try again.")
            shutdown()
    except Exception as e:
        print("Welcome fellow traveler! You're one of the few who have made it this far." \
               "We have no idea how you got at this error, but we're glad you're here." \
               "Please report this error to the developer, and we'll try to fix it as soon as possible. Thank you for your patience!")
        print(e)

