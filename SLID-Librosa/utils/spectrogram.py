import os
import shutil
import librosa
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger


def generate_spectrogram(filename, input_path, output_path):
    y, sr = librosa.load(Path.joinpath(input_path, filename))
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
    log_S = librosa.amplitude_to_db(S)

    plt.figure(figsize=(6, 6))
    librosa.display.specshow(log_S, sr=sr)
    plt.savefig(Path.joinpath(output_path, f"{filename}.png"), bbox_inches="tight")
    plt.close()

    logger.trace(f"File {filename}, saved to {output_path}")


def normalize_spectrogram(filename, spectrogram_path):
    language = filename[:2]
    language_dir_path = Path.joinpath(spectrogram_path, language)
    source = Path.joinpath(spectrogram_path, f"{filename}.png")
    destination = Path.joinpath(language_dir_path, f"{filename}.png")

    try:
        if Path(language_dir_path).exists():
            shutil.move(source, destination)
        else:
            os.mkdir(language_dir_path)
            shutil.move(source, destination)

        logger.trace(f"File {filename} moved to {language_dir_path}")
    except Exception as e:
        logger.error(e)
