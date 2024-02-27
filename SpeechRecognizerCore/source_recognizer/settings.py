import json
from pathlib import Path

import eel

ROOT_PATH = Path(__file__).parent.parent.absolute();
SETTINGS_PATH = Path(ROOT_PATH, "settings")


def get_settings():
    with open(Path(SETTINGS_PATH, "settings.json"), "r") as settings_file:
        settings: dict = json.load(settings_file)
        general_settings: dict = settings["general"]
    return general_settings
