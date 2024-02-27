import os
import json
import yaml
from pathlib import Path
from loguru import logger

ROOT_PATH = Path(__file__).parent.parent.absolute()
SETTINGS_PATH = Path(ROOT_PATH, "settings")
LID_SETTINGS_PATH = Path(SETTINGS_PATH, "language_identification")
DATA_STORE = "/mnt/data_store"


class LanguageIdentificationSettings:
    def __init__(self, config_path: str = LID_SETTINGS_PATH, config_file: str = "config.yml"):
        with open(Path(config_path, config_file), "r") as settings:
            settings: dict = yaml.safe_load(settings)
            self.lid_settings_path = LID_SETTINGS_PATH
            self.data_store_path = Path(ROOT_PATH, "data_store")
            self.models_dir_path = Path(DATA_STORE, "lid-models")

            self.lid_dataset = settings["lid_dataset"]
            self.lid_model: list = settings["lid_model"]

        with open(Path(SETTINGS_PATH, "settings.json"), "r") as json_file:
            json_settings: dict = json.load(json_file)
            identification = json_settings["identification"]
            model: dict = identification["model"]

            is_remote = model["is_model_remote"]

            if is_remote:
                model_name = model["model_remote"].split("/")[-1]
                self.model_file_path = Path(self.models_dir_path, model_name)
            else:
                path_to_model = Path(model["model_local"])
                if path_to_model.is_absolute():
                    self.model_file_path = path_to_model
                else:
                    self.model_file_path = Path(self.models_dir_path, path_to_model)

            self.languages: list = list(identification["lang_tag"].keys())
            self.language_tags: dict = identification["lang_tag"]

    @property
    def get_train_data_path_abs(self) -> str:
        """
        Method to get absolute path of train data directory
        :return: str
        """
        return Path(self.lid_dataset["path"], self.lid_dataset["train_dir"]).absolute()

    @property
    def get_test_data_path_abs(self) -> str:
        """
        Method to get absolute path of test data directory
        :return: str
        """
        return Path(self.lid_dataset["path"], self.lid_dataset["test_dir"]).absolute()


lid_settings = LanguageIdentificationSettings()

if __name__ == "__main__":
    logger.debug(ROOT_PATH)
    logger.debug(SETTINGS_PATH)
