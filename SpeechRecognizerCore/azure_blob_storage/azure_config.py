import json
import os

SETTINGS_PATH = './settings/settings.json'


def get_azure_credentials() -> dict | None:
    if not os.path.exists(SETTINGS_PATH):
        raise f"Failed to get azure settings - there is no settings.json file by path {SETTINGS_PATH}"
    with open(SETTINGS_PATH, 'r') as file:
        try:
            settings: dict = json.load(file)
            return settings.get('azure_api', None)
        except json.JSONDecodeError as e:
            raise f"Failed to get azure settings - corrupted data in settings.json"
