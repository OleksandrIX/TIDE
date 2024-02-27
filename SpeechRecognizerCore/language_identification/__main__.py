from loguru import logger
from config.variables import init_logger


def train_lid_model():
    from models.lid_model import LidModelTrainAndTest

    lid_model = LidModelTrainAndTest()
    lid_model.train_model()


def test_language_identification():
    import time
    from models.lid_model import LidModel

    lid_model = LidModel()

    path_to_audio = ""
    while path_to_audio.lower() != "q":
        time.sleep(1)
        path_to_audio = input("Enter path to audio file (or 'q' for exit): ")

        if path_to_audio.lower() == "q":
            break

        logger.info("Starting detect language...")
        language_probabilities, language, language_tags = lid_model.predict_language(path_to_audio)
        logger.info(f"Probabilities: {language_probabilities}")
        logger.info(f"Language: {language}")
        logger.info(f"Language tags: {language_tags}")


def print_all_settings():
    from config.variables import LanguageIdentificationSettings

    lid_settings = LanguageIdentificationSettings()
    logger.info(f"Languages: {lid_settings.languages}")
    logger.info(f"Languages file: {lid_settings.language_file_path}")
    logger.info(f"Train data dir: {lid_settings.get_train_data_path_abs}")
    logger.info(f"Test data dir: {lid_settings.get_test_data_path_abs}")
    logger.info(f"Stable model: {lid_settings.model_file_path}")
    logger.info(f"Models dir: {lid_settings.models_dir_path}")


def init_module():
    init_logger(app_name="language-identification",
                std_level="TRACE",
                file_level="INFO",
                log_rotation="12:00",
                log_compression="gz")
    print_all_settings()


if __name__ == "__main__":
    init_module()

    # Init LID model for testing
    # test_language_identification()

    # Train LID model
    # train_lid_model()
