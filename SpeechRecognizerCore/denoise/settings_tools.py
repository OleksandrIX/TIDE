import os
import json
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.absolute()
SETTINGS_PATH = Path(ROOT_PATH, "settings")


def get_settings():
    with open(Path(SETTINGS_PATH, "settings.json"), "r") as json_file:
        json_settings: dict = json.load(json_file)
        denoise_settings = json_settings["denoise"]

    return denoise_settings
