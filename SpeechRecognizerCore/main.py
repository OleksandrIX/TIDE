import os
import sys

from pathlib import Path
from loguru import logger
from config.logger import init_logger


def setup_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), "web", "expose", "spy"))


def init_project():
    """
    This function initializes logger and adds paths to sys.path
    """
    init_logger(
        app_name="speech-recognizer-core",
        std_level="TRACE",
        file_level="INFO",
    )

    setup_path()

    spy_dir = Path("./data_store", "spy")
    if not spy_dir.exists():
        os.mkdir(spy_dir)
        logger.info("Directory 'spy' is created")

    logger.info("Project initialized")


def init_ui():
    # Don't Remove It
    import web.expose.index
    import eel

    eel.init("web")
    eel.start("main.html", size=(1920, 1080))


def main():
    init_project()
    init_ui()


if __name__ == "__main__":
    main()
