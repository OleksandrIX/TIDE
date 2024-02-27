import os
import shutil
from tkinter import W
import eel
import json
from pathlib import Path

import pyaudio
from loguru import logger

from speech_recognizer.config import get_model_path
from speech_recognizer.speech_ways import SpeechWays
from web.expose.file_diaolog import get_dir

ROOT_PATH = Path(__file__).parent.parent.parent.absolute()
SETTINGS_DIR_PATH = Path(ROOT_PATH, "settings")
UI_DEFAULT_SETTINGS_PATH = Path(SETTINGS_DIR_PATH, "ui_default_settings.json")
SETTINGS_PATH = Path(SETTINGS_DIR_PATH, "settings.json")


def read_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return "".join(file.readlines())


def read_json(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@eel.expose
def get_ui_default_settings():
    return read_file(UI_DEFAULT_SETTINGS_PATH)


@eel.expose
def get_settings():
    if os.path.isfile(SETTINGS_PATH):
        return read_file(SETTINGS_PATH)
    else:
        return {}


@eel.expose
def save_settings(data):
    write_json(SETTINGS_PATH, data)


@eel.expose
def save_part_settings(id, data):
    json = {}
    if os.path.isfile(SETTINGS_PATH):
        json = read_json(SETTINGS_PATH)

    json[id] = data

    write_json(SETTINGS_PATH, json)


@eel.expose
def get_list_dir(path):
    path = get_model_path()
    return [o for o in os.listdir(path) if os.path.isdir(os.path.join(path, o))]


@eel.expose
def add_dir(root_path):
    from os import path

    selected_dir: str = get_dir()
    if not path.exists(selected_dir):
        return

    sphinx_path = get_model_path()

    try:
        shutil.copytree(selected_dir, path.join(sphinx_path, path.basename(selected_dir)))
        logger.info(f"Successfully uploaded language model - {path.basename(selected_dir)}")
    except shutil.SameFileError:
        logger.warning("Trying to copy the same file")
    except FileExistsError:
        logger.warning("Trying to copy file already exists")


@eel.expose
def remove_dir(root_path, dir_name):
    from os import path

    shutil.rmtree(path.join(root_path, dir_name))
    logger.info(f"Successfully removed language model - {path.join(root_path, dir_name)}")


@eel.expose
def get_microphones():
    import pyaudio

    arr = []

    try:

        py_audio = pyaudio.PyAudio()

        default_device_index = py_audio.get_default_input_device_info().get("index")
        device_info = py_audio.get_device_info_by_index(default_device_index)
        default_device_name = device_info["name"]

        arr.append(
            {
                "name": f"({default_device_index}) {default_device_name} (System default)",
                "value": device_info["name"],
                "index": default_device_index
            }
        )

        for i in range(py_audio.get_device_count()):
            device_info = py_audio.get_device_info_by_index(i)
            if (
                    device_info["maxInputChannels"] > 0
                    and device_info["name"] != default_device_name
            ):
                arr.append(
                    {
                        "name": f"({i}) {device_info['name']}",
                        "value": device_info["name"],
                        "index": i
                    }
                )

    finally:
        py_audio.terminate()
        return arr


def get_speech_way() -> str:
    settings_str: str = get_settings()
    settings: dict = json.loads(settings_str)
    speech_ways = settings.get('api', 'SPHINX')

    for speech_way in speech_ways:
        if speech_ways[speech_way]:
            return speech_way
