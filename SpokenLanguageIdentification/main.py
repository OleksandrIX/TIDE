import os
from loguru import logger
from pathlib import Path
from config.logger import init_logger


def train_lid_model():
    from models.lid_model import LidModelTrainAndTest

    lid_model = LidModelTrainAndTest()
    # lid_model.train_model(is_checkpoint=True, path_to_checkpoint="/home/azureuser/CNNModel-5-48.43.pth")


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
    from config.lid_config import LanguageIdentificationSettings

    lid_settings = LanguageIdentificationSettings()
    logger.info(f"Languages: {lid_settings.languages}")
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


def extract_model():
    import torch
    from models.lid_model import CNNModel
    path_to_checkpoint = "D:\\TIDE\\CNNModel-5-67.31.pth"

    device = torch.device("cpu")
    path_to_src_dir = os.path.dirname(path_to_checkpoint)
    filename = f"final_{os.path.basename(path_to_checkpoint)}"
    path_to_saved_model = os.path.join(path_to_src_dir, filename)

    checkpoint = torch.load(path_to_checkpoint, map_location=device)
    model = CNNModel(amount_languages=6).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    epoch = checkpoint["epoch"]

    torch.save(model.state_dict(), path_to_saved_model)
    logger.success(f"Saved final ({epoch} epochs) model to {[path_to_saved_model]}")


def main():
    init_module()
    extract_model()
    # train_lid_model()


if __name__ == "__main__":
    main()

    # Init LID model for testing
    # test_language_identification()

    # Train LID model
    # train_lid_model()
