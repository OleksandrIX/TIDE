import eel

from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent.absolute()
LOGS_DIR_PATH = Path(ROOT_PATH, "logs")
LOGS_PATH = Path(LOGS_DIR_PATH, "speech-recognizer-core.log")


@eel.expose
def get_logs():
    with open(LOGS_PATH, "r", encoding="utf-8") as file:
        logs = file.readlines()
        return logs
