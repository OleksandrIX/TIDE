from argparse import ArgumentParser
from loguru import logger
from utils.converter import convert_to_wav


def setup_logger():
    """
    Setup logger for application. Use loguru library.
    :return: None
    """
    from config.logger import init_logger

    init_logger(app_name="converter-to-wav",
                std_level="TRACE",
                file_level="INFO",
                log_rotation="12:00",
                log_compression="gz")


def arg_parser() -> tuple:
    """
    Parse arguments from command line.
    :return: tuple with source path and destination path
    """
    parser = ArgumentParser(description="Process some files.")
    parser.add_argument("-p", "--source_path", type=str, help="Source path")
    parser.add_argument("-d", "--destination_path", type=str, help="Destination path with audio name")

    args = parser.parse_args()
    src = args.source_path
    dst = args.destination_path

    return (src, dst)


if __name__ == "__main__":
    setup_logger()
    src, dst = arg_parser()
    logger.debug(f"Source path: {src}")
    logger.debug(f"Destination path: {dst}")
    convert_to_wav(src, dst)
