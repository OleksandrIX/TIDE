from sys import stderr
from loguru import logger
from pathlib import Path

LOG_DIR_PATH = Path(__file__).parent.parent / "logs"
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSSZZ}</green> "
    "| <level>{level:>8}</level> "
    "| <cyan>[{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}]</cyan> "
    "--- <level>{message}</level>"
)


def init_logger(app_name: str, std_level: str, file_level: str, log_rotation: str, log_compression: str):
    log_file_path = f"{LOG_DIR_PATH}/{app_name}.log"

    logger.remove()

    logger.add(
        stderr,
        format=LOG_FORMAT,
        level=std_level,
    )

    logger.add(
        log_file_path,
        format=LOG_FORMAT,
        level=file_level,
        rotation=log_rotation,
        compression=log_compression
    )

    logger.debug("Logger initialized.")
