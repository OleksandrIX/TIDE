import json
import os
from pathlib import Path

import eel

from os import path
from loguru import logger
import pipeline
from exceptions.InternalError import InternalError
from sources.response import Response
from speech_recognizer.speech_ways import SpeechWays
from web.expose.settings import get_speech_way

DATA_STORE_PATH = "./data_store"
SPEECH_FOLDER_NAME = "speech"
DIARIZATION_FOLDER_NAME = "diarization"


@eel.expose
def get_speech_for_file(folder_name: str,
                        file_name: str):
    """ Returns speech if file present """
    speech_file_name = Path(file_name).with_suffix(".txt")
    end_path = path.join(DATA_STORE_PATH, folder_name, SPEECH_FOLDER_NAME, speech_file_name)
    if not path.exists(end_path):
        return Response(404, {"message": f"Speech for file {file_name} was not found"}).to_dict()

    with open(end_path, 'r') as file:
        return Response(200, {"data": file.read()}).to_dict()


@eel.expose
def get_speeches_for_diarized_data(language_tags: list[str],
                                   folder_name: str,
                                   file_name: str):
    """
    Returns array of string with the speeches from diarized data
    Must be called after diarization
    """
    file_core = Path(file_name).with_suffix("").name
    files: list[str] = [file for file in os.listdir(path.join(DATA_STORE_PATH, folder_name, DIARIZATION_FOLDER_NAME))
                        if file.startswith("diarization_" + file_core) and file.endswith(".wav")]

    files.sort(key=lambda x: float(x[x.find(".rttm_") + len(".rttm_"):].split("_")[0]))
    speeches: list[str] = []

    speech_way: SpeechWays = SpeechWays(get_speech_way())

    for file in files:
        try:
            if language_tags[0] == 'AUTO':
                tags = get_language_tags_for_diarized_data(folder_name, file)
            else:
                tags = [language_tags[0]]

            speeches.append(pipeline.speech_recognizer(tags,
                                                       folder_name,
                                                       file,
                                                       speech_way,
                                                       additional_folder="diarization"))
        except InternalError as ie:
            return Response(500, {"message": str(ie)}).to_dict()

    return Response(200, {"speeches": speeches}).to_dict()


def get_language_tags_for_diarized_data(folder_name: str,
                                        file_name: str):
    """ Дуже сильний костиль """
    path_to_predict_json = Path(DATA_STORE_PATH, folder_name, "language",
                                Path("prediction_" + path.basename(file_name)).with_suffix(".json"))

    if not path.exists(path_to_predict_json):
        raise "Failed to get predict json file"

    with open(path_to_predict_json, 'rb') as file:
        language_json: dict = json.loads(file.read())
        return language_json.get("language_tags")


@eel.expose
def get_speech_part_for_file(folder_name: str,
                             file_name: str):
    """ Returns list[str] with speech parts if file is presented """
    end_path = path.join(DATA_STORE_PATH, folder_name, "speech")
    start_name = Path(file_name).with_suffix("").name
    file_names = [file for file in os.listdir(end_path)
                  if file.startswith("diarization_" + start_name) and file.endswith('.txt')]

    file_names.sort(key=lambda x: float(x[x.find(".rttm_") + len(".rttm_"):].split("_")[0]))

    speeches: list[str] = []
    for file_name in file_names:
        with open(path.join(DATA_STORE_PATH, folder_name, "speech", file_name), 'r') as file:
            speeches.append(file.read())
    return Response(200, {"speeches": speeches}).to_dict()
