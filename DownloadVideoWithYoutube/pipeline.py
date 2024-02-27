import os
import argparse
import shutil
from yaml import load, FullLoader
from loguru import logger
from config import logger as logger_config
from utils.ExtendedDict import ExtendedDict
from utils.download_youtube import download_user_and_playlist
from utils.normalise import normalise
from utils.wav_to_spectrogram import directory_to_spectrograms
from utils.delete_bad_images import delete_bad_images
from utils.organise_spectograms import organise

logger_config.init_logger()
config = load(open("config.yml", "rb"), Loader=FullLoader)


def pipeline(output_path, max_downloads):
    """
    The pipeline does the following:
    - downloads dataset
    - normalises the audio
    - converts audio to spectrograms
    - deletes bad spectrograms
    - organises the dataset for feeding it to NN
    """

    segmented = os.path.join(output_path, "segmented")
    unorg_spectrograms = os.path.join(output_path, "unorg_spectrograms")
    org_spectrograms = os.path.join(output_path, "org_spectrograms")

    logger.info("Youtube download started!")
    download_user_and_playlist(output_path, max_downloads)

    # deletes the folder with the unsegmented audio files
    shutil.rmtree(os.path.join(output_path, "raw"))

    # normalisation of segmented audio files
    logger.info("Loudness normalisation of segmented audio files started!")
    args = ExtendedDict({"source": segmented})
    normalise(args)

    # segmented wav files to spectrograms
    logger.info("Conversion of segmented wav files to spetrograms started!")
    args = ExtendedDict({
        "shape": config["input_shape"],
        "pixel_per_second": config["pixel_per_second"],
        "languages": config["label_names"],
        "source": segmented,
        "target": unorg_spectrograms
    })
    directory_to_spectrograms(args)

    # delete corrupted spectrograms
    logger.info("Deletion of bad spectrogram images started!")
    args = ExtendedDict({'source': unorg_spectrograms})
    delete_bad_images(args)

    # organise spectrograms by their classes and training, validation and test sets
    # in order to use the ImageDataGenerator's flow_from_directory()

    logger.info("Started organising spectrograms!")
    args = ExtendedDict({
        "source": unorg_spectrograms,
        "target": org_spectrograms
    })
    organise(args)
    shutil.rmtree(unorg_spectrograms)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", dest="output_path", default=os.getcwd(), required=True)
    parser.add_argument("--downloads", dest="max_downloads", default=1200)
    args = parser.parse_args()

    pipeline(args.output_path, args.max_downloads)
