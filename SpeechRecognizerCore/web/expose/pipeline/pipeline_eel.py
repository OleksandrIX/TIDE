import os
import json
from pathlib import Path
import eel
import pipeline
from glob import glob
from pathlib import Path
from exceptions.InternalError import InternalError
from sources.response import Response
from speech_recognizer.config import get_allowed_languages_for_sphinx, get_allowed_languages_for_whisper
from speech_recognizer.speech_ways import SpeechWays
from web.expose.settings import get_speech_way
from loguru import logger
from config import variables

ROOT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
SETTINGS_PATH = Path(ROOT_PATH, "settings")


@eel.expose
def get_settings_denoise():
    with open(Path(SETTINGS_PATH, "settings.json"), "r") as json_file:
        json_settings: dict = json.load(json_file)
        denoise_settings = json_settings["denoise"]

    return denoise_settings


@eel.expose
def set_settings_denoise(name: str, status: bool):
    with open(Path(SETTINGS_PATH, "settings.json"), "r") as json_file:
        json_settings: dict = json.load(json_file)
        denoise_settings = json_settings["denoise"]
        denoise_settings[name] = status

    with open(Path(SETTINGS_PATH, "settings.json"), "w") as json_file:
        json.dump(json_settings, json_file)


@eel.expose
def denoise_audio(folder_name: str,
                  file_name: str):
    output_file_name = pipeline.denoise_audio(folder_name, file_name)

    return Response(200, {
        "file_name": output_file_name
    }).to_dict()


@eel.expose
def define_language(folder_name: str,
                    file_name: str):
    path_to_folder = Path(variables.DATA_STORE_PATH, folder_name)
    path_to_diarization_folder = Path(path_to_folder, "diarization", "*.wav")
    diarization_files = glob(str(path_to_diarization_folder), recursive=True)
    diarization_files = [
        diarization_file
        for diarization_file in diarization_files
        if Path(diarization_file).parts[-1].startswith(f"diarization_{os.path.splitext(file_name)[0]}")
    ]

    files = []

    for diarization_file in diarization_files:
        parts = Path(diarization_file).parts
        diarization_file_name = parts[-1]

        (all_predictions,
         max_probability,
         language_tags) = pipeline.language_identification_with_audio(folder_name, diarization_file_name)

        files.append({
            "file_name": diarization_file_name,
            "all_predictions": all_predictions,
            "max_probability": max_probability,
            "language_tags": language_tags
        })

    return Response(200, body=files).to_dict()


@eel.expose
def recognize_speech(language_tags: list[str],
                     folder_name: str,
                     file_name: str):
    try:
        speech_way: SpeechWays = SpeechWays(get_speech_way())

        speech: str = pipeline.speech_recognizer(language_tags,
                                                 folder_name,
                                                 file_name,
                                                 speech_way)
    except InternalError as ei:
        return Response(500, {"message": str(ei)}).to_dict()
    except Exception as ex:
        return Response(500, {"message": str(ex)}).to_dict()

    return Response(200, {"text": speech}).to_dict()


@eel.expose
def diarization_audio(folder_name: str,
                      file_name: str,
                      min_diarization_speakers,
                      max_diarization_speakers):
    output_file_name = pipeline.diarization_audio(folder_name,
                                                  file_name,
                                                  min_diarization_speakers,
                                                  max_diarization_speakers)

    return Response(200, {
        "file_name": output_file_name
    }).to_dict()


@eel.expose
def get_manual_language() -> list[str]:
    """ Returns list of available languages for speech recognition
     depending on the model we are using:
      sphinx, whisper etc"""
    speech_way: SpeechWays = SpeechWays(get_speech_way())
    logger.debug(f"Getting language for {speech_way}")
    match speech_way:
        case SpeechWays.SPHINX:
            return get_allowed_languages_for_sphinx()
        case SpeechWays.WHISPER:
            return get_allowed_languages_for_whisper()
        case _:
            raise "Unknown way to recognize speech"
