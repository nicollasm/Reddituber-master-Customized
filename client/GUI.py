# import webbrowser
from pathlib import Path

import tomlkit
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

import utils.gui_utils as gui
from main import run
from utils.imagenarator import smart_MText
from PIL import ImageFont

# Set the hostname
HOST = "localhost"
# Set the port number
PORT = 4000

# Configure application
app = Flask(__name__, template_folder="GUI")

# Configure secret key only to use 'flash'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Display index.html
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recent")
def recent():
    return render_template("recent.html", file="videos.json")

@app.route('/update-image')
def update_image():
    value = request.args.get('value')
    color = "black" if request.args.get('color') == "undefined" else request.args.get('color')
    print(color)

    path = "GUI/tmp/tempimg.png"

    # smart_MText(
    #     "Your text will be displayed here",
    #     500,
    #     ImageFont.truetype("fonts/Roboto-Regular.ttf", 40),
    #     path,
    #     color,
    #     "white"
    # )
    return "tmp/tempimg.png"

@app.route("/run" ,methods=["POST","GET"])
def run_main():
    if request.method == "POST":
        run()
    return redirect(url_for("home"))

@app.route("/backgrounds", methods=["GET"])
def backgrounds():
    return render_template("backgrounds.html", file="backgrounds.json")


@app.route("/background/add", methods=["POST"])
def background_add():
    # Get form values
    youtube_uri = request.form.get("youtube_uri").strip()
    filename = request.form.get("filename").strip()
    citation = request.form.get("citation").strip()
    position = request.form.get("position").strip()

    gui.add_background(youtube_uri, filename, citation, position)

    return redirect(url_for("backgrounds"))

    
        
# @app.route("/")
# def main_page():
#     return render_template("/reddituber.html")


@app.route("/background/delete", methods=["POST"])
def background_delete():
    key = request.form.get("background-key")
    gui.delete_background(key)

    return redirect(url_for("backgrounds"))


@app.route("/settings", methods=["GET", "POST"])
def settings():
    config_load = tomlkit.loads(Path("config.toml").read_text())
    config = gui.get_config(config_load)

    # Get checks for all values
    checks = gui.get_checks()

    if request.method == "POST":
        # Get data from form as dict
        data = request.form.to_dict()

        # Change settings
        config = gui.modify_settings(data, config_load, checks)

    return render_template(
        "settings.html", file="config.toml", data=config, checks=checks
    )


# Make videos.json accessible
@app.route("/videos.json")
def videos_json():
    return send_from_directory("video_creation/data", "videos.json")


# Make backgrounds.json accessible
@app.route("/backgrounds.json")
def backgrounds_json():
    return send_from_directory("utils", "backgrounds.json")


# Make videos in results folder accessible
@app.route("/results/<path:name>")
def results(name):
    return send_from_directory("results", name, as_attachment=True)


# Make voices samples in voices folder accessible
@app.route("/voices/<path:name>")
def voices(name):
    return send_from_directory("GUI/voices", name, as_attachment=True)


#dddsdd



# Run browser and start the app
if __name__ == "__main__":
    # webbrowser.open(f"http://{HOST}:{PORT}", new=1)
    print("Website opened in new tab. Refresh if it didn't load.")
    app.run(port=PORT, debug=True)
#