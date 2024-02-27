import librosa
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger
from config.lid_config import lid_settings


def generate_spectrogram(filename: str, path_to_audio: str, folder_name: str) -> str:
    """
    This function generates a spectrogram
    :param folder_name: name of the folder to save the spectrogram
    :param filename: name of the audio file
    :param path_to_audio: path to the audio file
    :return: path to the spectrogram audio file
    """
    y, sr = librosa.load(path_to_audio)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    log_S = librosa.amplitude_to_db(S)
    plt.figure(figsize=(6, 6))
    librosa.display.specshow(log_S, sr=sr)

    image_path = Path(lid_settings.data_store_path, folder_name, "language", filename)
    plt.savefig(image_path, bbox_inches="tight")
    plt.close()

    logger.success(f"Spectrogram saved to {image_path}")
    return image_path
