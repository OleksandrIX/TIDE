import eel
from loguru import logger

from azure_blob_storage import is_connected
from azure_blob_storage.azure_worker import upload_folder
from sources.response import Response


@eel.expose
def is_azure_connected() -> Response:
    try:
        connected = is_connected()
    except Exception as ex:
        message = f"Failed to connect to Azure - {str(ex)}"
        logger.error(message)
        return Response(500, {"message": message}).to_dict()

    return Response(200, {"is_connected": connected}).to_dict()


@eel.expose
def upload_folder_to_azure(folder_name: str) -> Response:
    try:
        upload_folder(folder_name)
        return Response(200, {}).to_dict()
    except Exception as ex:
        return (Response(500, {"message": f"Failed to upload folder {folder_name} to Azure - {str(ex)}"})
                .to_dict())
