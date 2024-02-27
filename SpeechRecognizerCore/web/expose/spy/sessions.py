import os
import eel
import datetime
import spy_utils
import shutil
from pathlib import Path
from loguru import logger
from sources.response import Response
from exceptions.InternalError import InternalError

DATA_STORE_PATH = "./data_store/"


@eel.expose
def list_sessions_in_spy():
    sessions = []
    spy_path = Path(DATA_STORE_PATH, "spy")

    if not spy_path.exists():
        return Response(status=404,
                        body={"message": "Directory 'spy' not found"}).to_dict()

    try:
        sessions_dir = [session_dir for session_dir in os.listdir(spy_path) if
                        os.path.isdir(Path(spy_path, session_dir))]

        for session_dir in sessions_dir:
            session_path = Path(spy_path, session_dir)
            info = spy_utils.read_session_info(session_path)
            audio_files = spy_utils.get_all_audio_files_in_session(session_path)
            sessions.append({
                "session_id": session_dir,
                "info": info,
                "audio_files": audio_files
            })

        sessions = sorted(sessions, key=lambda session: session["info"]["created_at"], reverse=True)
        return Response(status=200, body={"sessions": sessions}).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def create_session(session):
    spy_path = Path(DATA_STORE_PATH, "spy")

    try:
        path_to_session_dir = spy_utils.creat_session_dir(spy_path)
        spy_utils.write_default_session_info(path_to_session_dir, session)
        spy_utils.create_session_log_file(path_to_session_dir)
        return Response(status=201, body={"message": "Session created"}).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def get_session_by_id(session_id):
    spy_path = Path(DATA_STORE_PATH, "spy")
    session_dir = Path(spy_path, session_id)

    try:
        session_info = spy_utils.read_session_info(session_dir)
        audio_files = spy_utils.get_all_audio_files_in_session(session_dir)

        groups = {}

        for audio_file in audio_files:
            folder_name = Path(audio_file).parts[3]
            filename = Path(audio_file).name

            if folder_name not in groups:
                groups[folder_name] = []
            duration = spy_utils.get_duration_length(audio_file)

            groups[folder_name].append({'filename': filename, 'duration': duration})

        return Response(status=200, body={
            "session": session_info,
            "groups": groups,
            "audio_files": audio_files
        }).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def get_session_name_by_id(session_id):
    spy_path = Path(DATA_STORE_PATH, "spy")
    session_dir = Path(spy_path, session_id)
    try:
        info = spy_utils.read_session_info(session_dir)
        return Response(status=200, body={"name": info["name"]}).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def delete_session(session_id):
    spy_path = Path(DATA_STORE_PATH, "spy")
    session_dir = Path(spy_path, session_id)
    session_info = spy_utils.read_session_info(session_dir)

    try:
        if not session_info["is_active"]:
            shutil.rmtree(session_dir)
            logger.info(f"Session {session_id} has been deleted")
            return Response(status=200, body={"message": "Session has been deleted"})
        else:
            return Response(status=500, body={"message": "You cannot delete a session while it is running"}).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()
