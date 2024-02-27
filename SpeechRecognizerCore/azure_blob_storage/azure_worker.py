from azure.storage.blob import BlobServiceClient, ContainerClient, ExponentialRetry

from loguru import logger

from azure_blob_storage import azure_config
from config.variables import DATA_STORE_PATH


def get_azure_blob_client() -> BlobServiceClient:
    azure_credentials: dict = azure_config.get_azure_credentials()

    account_name: str | None = azure_credentials.get('azure_account_name', None)
    account_key: str | None = azure_credentials.get('azure_account_key', None)

    connect_str: str = (f"DefaultEndpointsProtocol=https;AccountName={account_name}"
                        f";AccountKey={account_key};EndpointSuffix=core.windows.net")

    faster_retry = ExponentialRetry(initial_backoff=1, increment_base=1)
    return BlobServiceClient.from_connection_string(conn_str=connect_str, retry_policy=faster_retry)


def get_azure_container_client() -> ContainerClient:
    azure_credentials: dict = azure_config.get_azure_credentials()
    container_name: str | None = azure_credentials.get('azure_container_name', None)
    azure_blob_client: BlobServiceClient = get_azure_blob_client()
    return azure_blob_client.get_container_client(container_name)


def is_connected() -> bool:
    try:
        blob_service_client: BlobServiceClient = get_azure_blob_client()
        blob_service_client.get_service_properties()
        return True
    except Exception as ex:
        logger.warning(f"Failed to connect to Azure - {ex}")
        return False


def get_all_files_from_folder(folder_name: str) -> list[str]:
    from pathlib import Path
    from os import path

    data_store_path = Path(path.join(DATA_STORE_PATH, folder_name))
    file_names: list[str] = []
    files_path = [path for path in data_store_path.rglob("*")]
    for file_path in files_path:
        if path.isfile(file_path):
            file_names.append('/'.join([part.replace("//", '') for part in file_path.parts]))

    return file_names


def upload_folder(folder_name: str) -> None:
    """ The whole file folder will be uploaded to Azure """

    import os

    container_client: ContainerClient = get_azure_container_client()

    file_names: list[str] = get_all_files_from_folder(folder_name)

    for file_name in file_names:
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                name = os.path.join(*file_name.split("/")[1:])
                blob_client = container_client.get_blob_client(name)
                blob_client.upload_blob(file, overwrite=True)
                logger.info(f"File {file_name} was successfully uploada to Azure")
        else:
            logger.error(f"Failed to upload file - file was not found {file_name}")
