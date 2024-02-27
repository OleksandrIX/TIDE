import base64
import datetime
import os
import shutil
from os import path
from pathlib import Path

import eel
from loguru import logger
from pydub import AudioSegment

from config.variables import DATA_STORE_PATH, ALLOWED_EXTENSIONS
from converter_to_wav.utils import converter
from sources.response import Response


@eel.expose
def get_audio_file_by_path(folder_name: str, file_path: str) -> dict:
    file_path = os.path.join(DATA_STORE_PATH, folder_name, file_path)

    if not path.exists(file_path):
        response = Response(status=404,
                            body={"message": f"Failed to get file from {file_path}"})
        return response.to_dict()

    audio = AudioSegment.from_file(file_path)

    body = {
        'path': os.path.abspath(file_path),
        'name': os.path.basename(file_path),
        'duration': len(audio) / 1000,
        'size': round(os.path.getsize(file_path) / 1024),
        'date': str(datetime.datetime.fromtimestamp(os.path.getctime(file_path)))
    }

    with open(file_path, 'rb') as file:
        body['data'] = f"data:audio/x-wav;base64,{base64.b64encode(file.read()).decode()}"

    response = Response(status=200,
                        body={"file": body})
    return response.to_dict()


@eel.expose
def list_data_store():
    directories = [d for d in os.listdir(DATA_STORE_PATH)
                   if os.path.isdir(os.path.join(DATA_STORE_PATH, d)) and d != "spy"]

    file_explorer = {}
    for d in directories:
        files: list[str] = os.listdir(path.join(DATA_STORE_PATH, d))
        files = [file for file in files if path.splitext(file)[-1] in ALLOWED_EXTENSIONS]
        file_explorer[d] = files

    return Response(status=200,
                    body={"file_explorer": file_explorer}).to_dict()


@eel.expose
def delete_file(directory_name, file_name):
    try:
        if "%2F" in directory_name:
            from urllib.parse import unquote
            directory_name = unquote(directory_name)

        os.remove(path.join(DATA_STORE_PATH, directory_name, file_name))

        rest_files = [file for file in os.listdir(path.join(DATA_STORE_PATH, directory_name))
                      if path.isfile(path.join(DATA_STORE_PATH, directory_name, file))]

        if len(rest_files) == 0:
            shutil.rmtree(path.join(DATA_STORE_PATH, directory_name))
    except Exception as e:
        return Response(500, {"message": str(e)}).to_dict()

    return Response(200, {}).to_dict()


@eel.expose
def upload_file(absolute_path):
    import shutil

    directory_name = Path(path.basename(absolute_path)).with_suffix("")

    if not path.exists(path.join(DATA_STORE_PATH, directory_name)):
        # If there is new file to store
        # Create new folder, create language, diarization etc. folders
        os.mkdir(path.join(DATA_STORE_PATH, directory_name))
        os.mkdir(path.join(DATA_STORE_PATH, directory_name, "language"))
        os.mkdir(path.join(DATA_STORE_PATH, directory_name, "diarization"))
        os.mkdir(path.join(DATA_STORE_PATH, directory_name, "speech"))
    try:
        if Path(absolute_path).suffix != ".wav":
            return converter.convert_to_wav(absolute_path,
                                            path.join(DATA_STORE_PATH, directory_name, path.basename(absolute_path)))

        shutil.copy(absolute_path, path.join(DATA_STORE_PATH, directory_name, path.basename(absolute_path)))

    except shutil.SameFileError:
        logger.warning("Trying to copy the same file")


@eel.expose
def get_language_image_file_data(folder_name: str,
                                 file_name: str,
                                 *args: str):
    file_path = os.path.join(DATA_STORE_PATH, folder_name, *[arg for arg in args],
                             Path(file_name).with_suffix('.png'))

    if not path.exists(file_path):
        response = Response(status=404,
                            body={"message": f"Failed to get file from {file_path}"})
        return response.to_dict()

    with open(file_path, 'rb') as file:
        try:
            data = f"data:image/jpeg;base64,{base64.b64encode(file.read()).decode()}"
        except Exception as e:
            logger.error(f"Failed to read data of image file {file_path} - {str(e)}")
            return Response(500, {"message": "Failed to read data from image"}).to_dict()

    return Response(200, {"data": data}).to_dict()


@eel.expose
def get_diarization_audio(folder_name: str,
                          file_name: str) -> dict:
    file_path = os.path.join(DATA_STORE_PATH, folder_name, "diarization", file_name)

    if not path.exists(file_path):
        response = Response(status=404,
                            body={"message": f"Failed to get file from {file_path}"})
        return response.to_dict()

    audio = AudioSegment.from_file(file_path)
    body = {
        'path': os.path.abspath(file_path),
        'name': os.path.basename(file_path),
        'duration': len(audio) / 1000,
        'size': round(os.path.getsize(file_path) / 1024)
    }

    with open(file_path, 'rb') as file:
        body['data'] = f"data:audio/x-wav;base64,{base64.b64encode(file.read()).decode()}"

    response = Response(status=200,
                        body={"file": body})
    return response.to_dict()
