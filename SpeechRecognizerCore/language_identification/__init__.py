from language_identification.models.lid_model import LidModel
from language_identification.config.lid_config import LanguageIdentificationSettings


def check_settings() -> None:
    """
    This function checks if all settings are correct
    :return: None
    """
    from loguru import logger
    from language_identification.config.lid_config import LanguageIdentificationSettings

    lid_settings = LanguageIdentificationSettings()
    logger.info(f"Languages: {lid_settings.languages}")
    logger.info(f"Languages file: {lid_settings.language_file_path}")
    logger.info(f"Train data dir: {lid_settings.get_train_data_path_abs}")
    logger.info(f"Test data dir: {lid_settings.get_test_data_path_abs}")
    logger.info(f"Stable model: {lid_settings.model_file_path}")
    logger.info(f"Models dir: {lid_settings.models_dir_path}")
