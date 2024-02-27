from pathlib import Path
from loguru import logger
from config.logger import init_logger

AUDIO_DATASET_PATH = Path("./dataset/audio").absolute()
SPECTROGRAM_DATASET_PATH = Path("./dataset/spectrogram").absolute()
PREDICT_PATH = Path("./dataset/predict").absolute()
MODELS_PATH = Path("./saved_models").absolute()
epochs = 1


def create_spectrogram_dataset():
    from os import listdir
    from utils.spectrogram import generate_spectrogram, normalize_spectrogram

    dirs = ["test", "train"]

    for directory in dirs:
        audio_path = Path.joinpath(AUDIO_DATASET_PATH, directory)
        spectrogram_path = Path.joinpath(SPECTROGRAM_DATASET_PATH, directory)
        files = listdir(audio_path)

        for file in files:
            try:
                generate_spectrogram(filename=file,
                                     input_path=audio_path,
                                     output_path=spectrogram_path)
            except Exception as e:
                logger.error(e)

        for file in files:
            try:
                normalize_spectrogram(filename=file,
                                      spectrogram_path=spectrogram_path)
            except Exception as e:
                logger.error(e)


def training():
    from model.lid_model import training_model

    saved_model_path = Path("./saved_models").absolute()

    training_model(data_path_train=Path.joinpath(SPECTROGRAM_DATASET_PATH, "small_train"),
                   data_path_test=Path.joinpath(SPECTROGRAM_DATASET_PATH, "test"),
                   epochs=epochs,
                   saved_model_path=saved_model_path)


def test_accuracy_step():
    from model.lid_model import test_accuracy
    test_accuracy(data_path_test=Path.joinpath(SPECTROGRAM_DATASET_PATH, "test"),
                  path_to_model=Path.joinpath(MODELS_PATH, "CNNModel-2024-02-05_08-08-53-85.56.pth"))


def predict_test():
    from model.lid_model import predict
    predict(path_to_predict=PREDICT_PATH,
            path_to_model=Path.joinpath(MODELS_PATH, "CNNModel-2024-02-05_08-08-53-85.56.pth"))


if __name__ == "__main__":
    init_logger(app_name="slid-librosa",
                std_level="TRACE",
                file_level="INFO",
                log_rotation="1 day",
                log_compression="zip")

    logger.info("Project initialized")

    # create_spectrogram_dataset()

    # logger.success("Training started")
    # training()
    # logger.success("Training finished")

    logger.success("Test accuracy started")
    test_accuracy_step()
    logger.success("Test accuracy finished")

    # logger.success("Predict started")
    # predict_test()
    # logger.success("Predict finished")
