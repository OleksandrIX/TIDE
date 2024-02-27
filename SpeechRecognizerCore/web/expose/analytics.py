import json

import eel
from os import path
from loguru import logger

from sources.response import Response

DATA_STORE_PATH = "./data_store"
STATISTIC_JSON_FILE_NAME = "statistic.json"


@eel.expose
def get_statistic() -> Response:
    statistic_json_file_path = path.join(DATA_STORE_PATH, STATISTIC_JSON_FILE_NAME)

    if not path.exists(statistic_json_file_path):
        message: str = f"Failed to load statistic.json file - File was not found {statistic_json_file_path}"
        logger.error(message)
        return Response(404, {"message": message}).to_dict()

    try:
        with open(statistic_json_file_path, 'r') as file:
            json_data = json.load(file)
    except json.JSONDecodeError:
        message: str = f"Failed to load statistic.json file - corrupted data"
        logger.error(message)
        return Response(500, {"message": message}).to_dict()

    logger.info("Analytics successfully loaded")
    return Response(200, {"statistic": json_data}).to_dict()
