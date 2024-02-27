import os
import eel
from glob import glob
from pathlib import Path
from config.variables import DATA_STORE_PATH
from sources.response import Response
from loguru import logger


@eel.expose
def get_diarization_file_by_path(folder_name: str, file_path: str) -> dict:
    file_path = Path(DATA_STORE_PATH, folder_name, "diarization",
                     f'diarization_{Path(file_path).with_suffix(".rttm")}')

    if not os.path.exists(file_path):
        response = Response(status=404,
                            body={"message": f"Failed to get    file from {file_path}"})
        return response.to_dict()

    files = glob(str(Path(os.path.dirname(file_path), f"{os.path.basename(file_path)}*.wav")))
    diarization_audio_files = [os.path.basename(audio_file) for audio_file in files]

    body = {
        'path': os.path.abspath(file_path),
        'name': os.path.basename(file_path),
        'diarization_audio_files': diarization_audio_files,
    }
    with open(file_path, 'r') as diarization_file:
        body['data'] = [line.replace('\n', '') for line in diarization_file.readlines()]

    response = Response(status=200,
                        body={"file": body})
    return response.to_dict()
