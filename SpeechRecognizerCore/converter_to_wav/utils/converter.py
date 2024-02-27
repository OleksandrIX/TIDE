from pathlib import Path

from pydub import AudioSegment, effects
from loguru import logger


def convert_to_wav(src: str, dst: str) -> None:
    """
    Convert any audio file to wav format.
    :param src: path to audio file
    :param dst: path to destination file
    :return: None
    """
    try:
        sound = AudioSegment.from_file(src)
        sound = effects.normalize(sound)
        sound.export(Path(dst).with_suffix(".wav"), format="wav")
        logger.info(f"File {src} converted to {dst}")
    except Exception as err:
        logger.exception(f"{err=}, {type(err)=}")
