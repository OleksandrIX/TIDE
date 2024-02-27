from os import path
from pathlib import Path

import eel
from loguru import logger

from config.variables import DATA_STORE_PATH, PREDICTION_PREFIX, LANGUAGE_FOLDER_NAME
from sources.response import Response


@eel.expose
def get_prediction_language_for_file(folder_name: str,
                                     file_name: str):
    """
    Methods checks if language.json file present for given file_name
    and return Response to FE
    If file is not presented, returns 404
    """

    import json

    prediction_file_name = Path(path.basename(PREDICTION_PREFIX + file_name)).with_suffix(".json")
    path_to_file = path.join(DATA_STORE_PATH, folder_name, LANGUAGE_FOLDER_NAME, prediction_file_name)

    if not path.exists(path_to_file):
        return Response(404, {"message": f"File {path_to_file} was not found"}).to_dict()

    with (open(path_to_file, 'r') as file):
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            logger.error(f"Corrupted JSON data in file {path_to_file}")
            return Response(500, {"message": f"File {path_to_file} has corrupted data"}).to_dict()

    return Response(200, {"file": data}).to_dict()
