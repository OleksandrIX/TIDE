import os
import librosa
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger
from language_identification.config.lid_config import lid_settings
from pydub import AudioSegment


def generate_spectrogram(filename: str, path_to_audio: str, folder_name: str) -> str:
    """
    This function generates a spectrogram
    :param folder_name: name of the folder to save the spectrogram
    :param filename: name of the audio file
    :param path_to_audio: path to the audio file
    :return: path to the spectrogram audio file
    """
    folder_path = Path(lid_settings.data_store_path, folder_name, "language")
    src_audio = AudioSegment.from_wav(path_to_audio)
    length_in_seconds = src_audio.duration_seconds

    if length_in_seconds > 10:
        path_to_audio = slice_audio(src_audio, folder_path, os.path.splitext(filename)[0])

    y, sr = librosa.load(path_to_audio)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    log_S = librosa.amplitude_to_db(S)
    plt.figure(figsize=(6, 6))
    librosa.display.specshow(log_S, sr=sr)

    image_path = Path(folder_path, filename)
    plt.savefig(image_path, bbox_inches="tight")
    plt.close()

    logger.success(f"Spectrogram saved to {image_path}")
    return image_path


def slice_audio(audio: AudioSegment, folder_path: Path, filename: str) -> str:
    audio = audio[:10 * 1000]
    path_to_segment = Path(folder_path, f"segment_{filename}.wav")
    audio.export(path_to_segment, format="wav")
    return path_to_segment
