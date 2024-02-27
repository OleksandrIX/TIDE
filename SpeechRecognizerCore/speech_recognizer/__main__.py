from loguru import logger
from config.variables import init_logger
from speech_recognizer import config


def execute_main():
    pass


def init_module():
    init_logger(app_name="speech-recognition",
                std_level="TRACE",
                file_level="INFO",
                log_rotation="12:00",
                log_compression="gz")


if __name__ == "__main__":
    init_module()

    logger.info("This is speech_recognition/__init__.py")
    logger.info(f"Allowed language models: {config.get_allowed_languages_for_sphinx()}")
