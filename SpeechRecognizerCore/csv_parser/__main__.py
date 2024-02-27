import os
from argparse import ArgumentParser
from os import path
from pathlib import Path

from loguru import logger

DATA_STORE_PATH = '../data_store'


def arg_parser() -> tuple:
    """
    Parse arguments from command line.
    :return: tuple with source path and destination path
    """
    parser = ArgumentParser(description="Process some files.")
    parser.add_argument("-p", "--folder_of_file_path", type=str, help="Path of main file's folder")
    parser.add_argument("-f", "--original_file_name", type=str, help="Name of original file")

    args = parser.parse_args()
    return args.folder_of_file_path, args.original_file_name


def get_diarization_files(folder_name: str,
                          file_name: str):
    logger.info("Collecting .rttm data")
    path_to_diarization_folder = path.join(DATA_STORE_PATH, folder_name, "diarization")

    logger.debug(f"path_to_diarization_folder - {path_to_diarization_folder}")

    file_name_start_with: str = "diarization_" + Path(file_name).with_suffix("").name

    logger.debug(f"file_name_start_with - {file_name_start_with}")

    return [f for f in os.listdir(path_to_diarization_folder)
            if f.startswith(file_name_start_with)]


def get_text_from_diarization_file(folder_name: str,
                                   rttm_file_name: str,
                                   start: str,
                                   end: str,
                                   speaker: str) -> str:
    cut_file_name = rttm_file_name + "_" + start + "_" + end + "_" + speaker + ".txt"

    path_to_file = Path(DATA_STORE_PATH, folder_name, "speech", cut_file_name)

    with open(path_to_file, 'r') as cut_file:
        return cut_file.read()


def main(folder_name: str,
         file_name: str):
    logger.debug(f"Starting collecting data from {folder_name} for {file_name}")

    if not path.exists(path.join(DATA_STORE_PATH, folder_name)):
        return logger.error("Failed to parse data - given directory does not exist")

    if not path.exists(path.join(DATA_STORE_PATH, folder_name, file_name)):
        return logger.error("Failed to parse data - given file does not exists")

    diarization_files: list[str] = get_diarization_files(folder_name, file_name)

    logger.info(f"Got .rttm files. Total {len(diarization_files)} files were found")

    if len(diarization_files) == 0:
        return logger.warning("There is no diarized files were provided")

    rttm_file_name = next((f for f in diarization_files if f.endswith('.rttm')), None)

    if not rttm_file_name:
        return logger.error("There is no .rttm file provided")

    with open(path.join(DATA_STORE_PATH, folder_name, "diarization", rttm_file_name), 'r') as rttm_file:
        rttm_lines = [line.replace('\n', '').strip() for line in rttm_file.readlines()]

    text = ""
    old_speaker = ""
    for line in rttm_lines:
        start, end, speaker = line.split(" ")
        if old_speaker != speaker:
            """ If different speaker - do new line """
            old_speaker = speaker
            text += f"\n{speaker},"

        """ Read text from cut files and write in `text` """
        diarization_text = get_text_from_diarization_file(folder_name, rttm_file_name, start, end, speaker)
        text += " " + diarization_text.lstrip()

    text = text.strip()
    pretty_text = ""
    """ Костилім, претіфаєм """
    for text_line in text.split("\n"):
        split_line_by_comma = text_line.split(',')
        pretty_text += split_line_by_comma[0] + "," + '"' + ",".join(split_line_by_comma[1:]) + '"\n'

    with open(path.join(DATA_STORE_PATH, folder_name, Path(file_name).with_suffix("").name + '.csv'), 'w') as csv_file:
        csv_file.write(pretty_text)

    logger.info("Successfully parsed to csv")


if __name__ == '__main__':
    # folder, file = arg_parser()
    main("2-3B-ENG-NS", "2-3B-ENG-NS.wav")
