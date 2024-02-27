import os
import json
import uuid
from glob import glob
from pathlib import Path
from pydub import AudioSegment

import eel
from loguru import logger
from datetime import datetime

ALLOWED_EXTENSIONS = ['.wav']


def read_session_info(session_path: Path):
    with open(Path(session_path, "info.json"), "r") as info:
        return json.load(info)


def get_all_audio_files_in_session(session_path: Path):
    audio_files = [glob(f"{str(session_path)}/*/*{extension}", recursive=True)
                   for extension in ALLOWED_EXTENSIONS]
    audio_files = [file for files in audio_files for file in files]
    audio_files.sort()
    return audio_files


def get_duration_length(file_path):
    audio_file = AudioSegment.from_file(file_path)
    duration = f"{audio_file.duration_seconds:.2f}"
    return duration


def creat_session_dir(spy_path: Path):
    session_id = str(uuid.uuid4())
    try:
        path_to_session_dir = Path(spy_path, session_id)
        os.mkdir(path_to_session_dir)
        return path_to_session_dir
    except FileExistsError:
        raise FileExistsError


def write_default_session_info(path_to_session_dir: Path, session_info: dict):
    session_info["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_info["is_active"] = False
    with open(Path(path_to_session_dir, "info.json"), "w", encoding="utf-8") as info_file:
        json.dump(session_info, info_file, indent=4)


def create_session_log_file(path_to_session_dir: Path):
    with open(Path(path_to_session_dir, "session.log"), "w", encoding="utf-8") as log_file:
        log_file.write("")


def update_session_info(path_to_session_dir: Path, **kwargs):
    path_to_info = Path(path_to_session_dir, "info.json")

    with open(path_to_info, "r", encoding="utf-8") as info_file:
        session_info = json.load(info_file)

    for field, value in kwargs.items():
        if field in session_info:
            session_info[field] = value
        else:
            logger.warning(f"Field {field} not found in session info")

    with open(path_to_info, "w", encoding="utf-8") as info_file:
        json.dump(session_info, info_file, indent=4)
