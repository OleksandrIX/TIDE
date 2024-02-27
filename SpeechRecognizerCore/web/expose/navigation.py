import os
import eel
from pathlib import Path
from glob import glob
from loguru import logger
from config.variables import DATA_STORE_PATH
from sources.response import Response


@eel.expose
def get_neighbors_audio(folder_name, file_name):
    path_to_folder = Path(DATA_STORE_PATH, folder_name)
    is_spy = len(path_to_folder.parts) > 2

    if not path_to_folder.exists():
        return Response(status=404, body={"message": "Folder not found"}).to_dict()

    try:
        if not is_spy:
            folders = get_folders(Path(DATA_STORE_PATH))
            (previous_audio,
             previous_audio_folder,
             next_audio,
             next_audio_folder) = get_audio_files(Path(DATA_STORE_PATH),
                                                  path_to_folder,
                                                  folders,
                                                  folder_name,
                                                  file_name)
        else:
            folder_parts = list(Path(folder_name).parts)
            current_session = folder_parts[1]
            current_session_folder = folder_parts[-1]

            session_folder_path = Path(DATA_STORE_PATH, "spy", current_session)

            if not session_folder_path.exists():
                return Response(status=404, body={"message": "Folder not found"}).to_dict()

            folders = get_folders(session_folder_path)
            (previous_audio,
             previous_audio_folder,
             next_audio,
             next_audio_folder) = get_audio_files(session_folder_path,
                                                  path_to_folder,
                                                  folders,
                                                  current_session_folder,
                                                  file_name)

            previous_audio_folder = f"spy/{current_session}/{previous_audio_folder}"
            next_audio_folder = f"spy/{current_session}/{next_audio_folder}"


        return Response(status=200, body={
            "previous_audio": previous_audio,
            "previous_audio_folder": previous_audio_folder,
            "next_audio": next_audio,
            "next_audio_folder": next_audio_folder
        }).to_dict()
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


def get_audio_files(src_folder_path, path_to_folder, folders, folder_name, file_name):
    files_in_current_folder = get_files(path_to_folder)

    file_index = files_in_current_folder.index(file_name)
    folder_index = folders.index(folder_name)

    (previous_audio,
     previous_audio_folder,
     next_audio,
     next_audio_folder) = get_previous_and_next_audio(src_folder_path,
                                                      folders,
                                                      files_in_current_folder,
                                                      file_index,
                                                      folder_index)

    return previous_audio, previous_audio_folder, next_audio, next_audio_folder


def get_previous_and_next_audio(src_folder_path, folders, files, file_index, folder_index):
    previous_audio, next_audio = None, None
    previous_audio_folder, next_audio_folder = None, None

    previous_file = files[file_index - 1] if file_index > 0 else None
    next_file = files[file_index + 1] if file_index < len(files) - 1 else None

    if not previous_file:
        previous_folder = folders[folder_index - 1] if folder_index > 0 else None

        if previous_folder:
            files_in_previous_folder = get_files(Path(src_folder_path, previous_folder))
            previous_audio = files_in_previous_folder[-1]
            previous_audio_folder = previous_folder
    else:
        previous_audio = previous_file
        previous_audio_folder = folders[folder_index]

    if not next_file:
        next_folder = folders[folder_index + 1] if folder_index < len(folders) - 1 else None

        if next_folder:
            files_in_next_folder = get_files(Path(src_folder_path, next_folder))
            next_audio = files_in_next_folder[0]
            next_audio_folder = next_folder
    else:
        next_audio = next_file
        next_audio_folder = folders[folder_index]

    return previous_audio, previous_audio_folder, next_audio, next_audio_folder


def get_files(path_to_folder):
    files = [
        file
        for file in os.listdir(path_to_folder)
        if Path(path_to_folder, file).is_file()
    ]
    files.sort(key=lambda x: x.lower())
    return files


def get_folders(path_to_folder):
    folders = [
        folder
        for folder in os.listdir(path_to_folder)
        if Path(path_to_folder, folder).is_dir() and folder != "spy"
    ]
    folders.sort(key=lambda x: x.lower())
    return folders
