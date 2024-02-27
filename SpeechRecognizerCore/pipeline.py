import os
import queue
from loguru import logger
from pathlib import Path
from glob import glob
from azure_blob_storage.azure_worker import upload_folder
from config.variables import DATA_STORE_PATH
from exceptions.InternalError import InternalError
from os import path

from speech_recognizer.config import get_language_name_from_bcp_47
from speech_recognizer.speech_ways import SpeechWays
from web.expose.settings import get_speech_way

lid_model = None
denoise_model = None
diarization_model = None


def init_lid_model():
    from language_identification import LidModel
    global lid_model

    try:
        lid_model = LidModel()
        logger.info("Initialized language identification model")
    except Exception as err:
        logger.error(f"{err=}")
        raise err


def init_denoise_model(model_architecture_path, model_weights_path):
    from denoise.load_model import load_model
    denoise_model = load_model(model_architecture_path, model_weights_path)

    logger.info("Initialized denoise model")

    return denoise_model


def init_diarization_model():
    from diarization.load_model import load_model
    diarization_model = load_model()
    logger.info("Initialized diarization model")

    return diarization_model


def denoise_audio(folder_name, file_name):
    from denoise import denoise, settings_tools

    audio_input_path = path.join(DATA_STORE_PATH, folder_name, file_name)

    model_weights_path = "./denoise/weights/model_unet.h5"
    model_architecture_path = "./denoise/weights/model_unet.json"

    global denoise_model

    if not denoise_model:
        denoise_model = init_denoise_model(model_architecture_path, model_weights_path)

    denoise_settings = settings_tools.get_settings()

    sample_rate = 8000
    frame_length = 8064
    hop_length_frame = 8064
    n_fft = 255
    hop_length_fft = 63

    is_model = denoise_settings.get("is_model", False)
    is_spectral_gating = denoise_settings.get("is_spectral_gating", False)
    volume = denoise_settings.get('volume', 2)

    output_filename = f"denoise_{path.basename(audio_input_path)}"
    audio_output_path = path.join(DATA_STORE_PATH, folder_name, output_filename)

    denoise(loaded_model=denoise_model,
            audio_input_noise=audio_input_path,
            audio_output_prediction=audio_output_path,
            sample_rate=sample_rate,
            frame_length=frame_length,
            hop_length_frame=hop_length_frame,
            n_fft=n_fft,
            hop_length_fft=hop_length_fft,
            volume=volume,
            is_model=is_model,
            is_spectral_gating=is_spectral_gating)

    return output_filename


def diarization_audio(folder_name, audio_input_path, min_diarization_speakers, max_diarization_speakers):
    from diarization import diarization

    global diarization_model

    if not diarization_model:
        diarization_model = init_diarization_model()
    output_filename = f"diarization_{Path(audio_input_path).with_suffix('.rttm')}"
    audio_input_path = path.join(DATA_STORE_PATH, folder_name, audio_input_path)
    audio_output_path = path.join(DATA_STORE_PATH, folder_name, "diarization", output_filename)

    diarization(audio_input_path=audio_input_path,
                pipeline=diarization_model,
                audio_output_path=audio_output_path,
                min_diarization_speakers=min_diarization_speakers,
                max_diarization_speakers=max_diarization_speakers)

    return output_filename


def language_identification_with_audio(folder_name: str,
                                       file_name: str):
    """
    This function detects language from audio file
    :param file_name str
    :param folder_name str
    :return: tuple, (audio_input_path, all_predictions, max_probability, language_tags)
    """
    from language_identification import LanguageIdentificationSettings

    audio_path = Path(DATA_STORE_PATH, folder_name, "diarization", file_name)

    global lid_model
    try:
        if not lid_model:
            init_lid_model()
        else:
            lid_settings = LanguageIdentificationSettings()
            if lid_model.model_file_path != lid_settings.model_file_path:
                init_lid_model()

        all_predictions, max_probability, language_tags = lid_model.predict_language(audio_path, folder_name)

        logger.info(f"All predictions: {all_predictions}")
        logger.info(f"Max probability: {max_probability}")
        logger.info(f"Language tags: {language_tags}")

        return all_predictions, max_probability, language_tags
    except:
        logger.warning("Language identification not loaded")
        return {}, "", []


def speech_recognizer(language_tags: list[str],
                      folder_name: str,
                      file_name: str,
                      speech_way: SpeechWays,
                      **kwargs):
    match speech_way:
        case SpeechWays.SPHINX:
            logger.info("Starting recognize text using Sphinx")
            text = recognize_using_sphinx(language_tags,
                                          folder_name,
                                          file_name,
                                          **kwargs)
        case SpeechWays.WHISPER:
            logger.info("Starting recognize text using Whisper")
            text = recognize_using_whisper(language_tags,
                                           folder_name,
                                           file_name,
                                           **kwargs)
        case _:
            text = ""
    return text


def recognize_using_sphinx(language_tags: list[str],
                           folder_name: str,
                           file_name: str,
                           **kwargs):
    import speech_recognizer
    import speech_recognition as sr

    languages: list[str] = speech_recognizer.text_reco_config.get_allowed_languages_for_sphinx()
    logger.info(f"Allowed language models: {languages}")

    common_languages: set = set(language_tags).intersection(set(languages))

    if len(common_languages) == 0:
        message = f"Failed to translate audio. {language_tags} languages aren't supported by speech_recognizer"
        logger.warning(message)
        raise InternalError(message)

    additional_folder: str = kwargs.get("additional_folder", None)
    if additional_folder:
        path_to_audio = path.join(DATA_STORE_PATH, folder_name, additional_folder, file_name)
    else:
        path_to_audio = path.join(DATA_STORE_PATH, folder_name, file_name)

    audio_file: sr.AudioFile = sr.AudioFile(filename_or_fileobject=path_to_audio)
    logger.debug(f"Reco speech. language: {list(common_languages)[0]}, SPHINX")
    text: str = speech_recognizer.speech_recognizer.recognize_sphinx(list(common_languages)[0],
                                                                     audio_file)

    logger.debug(f"AUDIO: {text}")

    speech_folder_name = "speech"
    output_filename: Path = Path(path.basename(path_to_audio)).with_suffix(".txt")
    audio_output_path = path.join(DATA_STORE_PATH, folder_name, speech_folder_name, output_filename)

    with open(audio_output_path, 'w') as output:
        output.write(text)

    logger.info(f"Result has been written to {audio_output_path}")
    return text


def recognize_using_whisper(language_tags: list[str],
                            folder_name: str,
                            file_name: str,
                            **kwargs):
    import speech_recognizer
    import speech_recognition as sr

    if any(lang.__contains__('-') for lang in language_tags):
        language: str = get_language_name_from_bcp_47(language_tags[0])
    else:
        if isinstance(language_tags, str):
            language = language_tags
        else:
            language = language_tags[0]

    additional_folder: str = kwargs.get("additional_folder", None)
    if additional_folder:
        path_to_audio = path.join(DATA_STORE_PATH, folder_name, additional_folder, file_name)
    else:
        path_to_audio = path.join(DATA_STORE_PATH, folder_name, file_name)

    audio_file: sr.AudioFile = sr.AudioFile(filename_or_fileobject=path_to_audio)
    logger.debug(f"Reco speech. language: {language}, WHISPER")
    text: str = speech_recognizer.speech_recognizer.recognize_whisper(language,
                                                                      audio_file)

    logger.debug(f"AUDIO: {text}")

    speech_folder_name = "speech"
    output_filename: Path = Path(path.basename(path_to_audio)).with_suffix(".txt")
    audio_output_path = path.join(DATA_STORE_PATH, folder_name, speech_folder_name, output_filename)

    with open(audio_output_path, 'wb') as output:
        output.write(text.encode("utf-8"))

    logger.info(f"Result has been written to {audio_output_path}")

    return text


def record_audio(destination_path,
                 recording_queue,
                 pipeline_queue,
                 notify_client_about_new_file,
                 notify_client_about_error):
    from source_recognizer import Recording
    recording = Recording()
    recording.start_recording(destination_path,
                              recording_queue,
                              pipeline_queue,
                              notify_client_about_new_file,
                              notify_client_about_error)


def get_folder_and_file_name(path_to_audio):
    path_to_audio = Path(path_to_audio)
    data_store_index = path_to_audio.parts.index("data_store")
    path_parts = path_to_audio.parts[data_store_index + 1:]
    folder_name = str(Path(*path_parts[0:-1]))
    file_name = path_parts[-1]

    return folder_name, file_name


class Pipeline:
    def __init__(self,
                 notify_client_about_completed_pipeline,
                 notify_client_about_error,
                 default_language_to_use,
                 is_auto_upload,
                 recording_queue,
                 pipeline_queue):
        self.lid_model = None
        self.denoise_model = None
        self.diarization_model = None

        self.__init_denoise_module()
        self.__init_lid_module()
        self.__init_diarization_module()

        self.notify_client_about_completed_pipeline = notify_client_about_completed_pipeline
        self.notify_client_about_error = notify_client_about_error

        self.default_language_to_use = default_language_to_use
        self.is_auto_upload = is_auto_upload

        self.recording_queue = recording_queue
        self.pipeline_queue = pipeline_queue

    def __init_denoise_module(self):
        from denoise import denoise, settings_tools
        model_weights_path = "./denoise/weights/model_unet.h5"
        model_architecture_path = "./denoise/weights/model_unet.json"
        self.denoise_model = init_denoise_model(model_architecture_path, model_weights_path)

    def __init_diarization_module(self):
        from diarization.load_model import load_model
        self.diarization_model = load_model()
        logger.info("Initialized diarization model")

    def __init_lid_module(self):
        from language_identification import LidModel
        self.lid_model = LidModel()
        logger.info("Initialized language identification model")

    def __denoise(self, folder_name, file_name):
        from denoise import denoise, settings_tools
        audio_input_path = path.join(DATA_STORE_PATH, folder_name, file_name)
        denoise_settings = settings_tools.get_settings()

        sample_rate = 8000
        frame_length = 8064
        hop_length_frame = 8064
        n_fft = 255
        hop_length_fft = 63

        is_model = denoise_settings.get("is_model", False)
        is_spectral_gating = denoise_settings.get("is_spectral_gating", False)
        volume = denoise_settings.get('volume', 2)

        output_filename = f"denoise_{path.basename(audio_input_path)}"
        audio_output_path = path.join(DATA_STORE_PATH, folder_name, output_filename)

        denoise(loaded_model=self.denoise_model,
                audio_input_noise=audio_input_path,
                audio_output_prediction=audio_output_path,
                sample_rate=sample_rate,
                frame_length=frame_length,
                hop_length_frame=hop_length_frame,
                n_fft=n_fft,
                hop_length_fft=hop_length_fft,
                volume=volume,
                is_model=is_model,
                is_spectral_gating=is_spectral_gating)

        return audio_output_path

    def __diarization(self, folder_name, file_name):
        from diarization import diarization
        output_filename = f"diarization_{Path(file_name).with_suffix('.rttm')}"
        file_name = path.join(DATA_STORE_PATH, folder_name, file_name)
        audio_output_path = path.join(DATA_STORE_PATH, folder_name, "diarization", output_filename)

        diarization(audio_input_path=file_name,
                    pipeline=self.diarization_model,
                    audio_output_path=audio_output_path,
                    min_diarization_speakers='AUTO',
                    max_diarization_speakers='AUTO')
        return audio_output_path

    def __language_identification(self, file_path, folder_name):
        return self.lid_model.predict_language(file_path, folder_name)

    def __azure_upload(self, folder_name):
        folder_path = Path(DATA_STORE_PATH, folder_name).name
        return upload_folder(folder_path)

    def start_pipeline(self):
        try:
            while True:
                if not self.pipeline_queue.empty():
                    path_to_audio = self.pipeline_queue.get()

                    if isinstance(path_to_audio, bool) and not path_to_audio:
                        break

                    logger.info("Pipeline started")

                    # Step 0: Extracting folder and file name from audio file path
                    folder_name, file_name = get_folder_and_file_name(path_to_audio)

                    # Step 1: DeNoise
                    path_to_audio = self.__denoise(folder_name, file_name)
                    folder_name, file_name = get_folder_and_file_name(path_to_audio)

                    # Step 2: Diarization
                    diarization_audio_path = self.__diarization(folder_name, file_name)
                    diarization_audio_files = glob(str(Path(os.path.dirname(diarization_audio_path),
                                                            f"{os.path.basename(diarization_audio_path)}*.wav")))

                    # Step 3: Recognize language (en, ua, es)
                    audio_and_language = []
                    if self.default_language_to_use == "AUTO":
                        logger.debug("Starting recognizing the language")
                        for audio_file in diarization_audio_files:
                            (all_predictions,
                             max_probability,
                             language_tags) = self.__language_identification(audio_file, folder_name)
                            logger.info(f"All predictions: {all_predictions}")
                            logger.info(f"Max probability: {max_probability}")
                            logger.info(f"Language tags: {language_tags}")
                            audio_and_language.append((audio_file, language_tags))
                    else:
                        logger.debug(f"Using language by default - {self.default_language_to_use}")
                        language_tags = [self.default_language_to_use]
                        audio_and_language = [(audio_file, language_tags)
                                              for audio_file in diarization_audio_files]

                    # Step 4: Recognize text
                    speech_way: SpeechWays = SpeechWays(get_speech_way())

                    for audio_file, language_tags in audio_and_language:
                        file_name = os.path.basename(audio_file)
                        speech_recognizer(language_tags=language_tags,
                                          folder_name=folder_name,
                                          file_name=file_name,
                                          speech_way=speech_way,
                                          additional_folder="diarization")

                    # Step 5: Upload to Azure
                    if self.is_auto_upload:
                        logger.info("Starting Azure Uploading")
                        self.__azure_upload(folder_name)

                    logger.info("Pipeline finished")
                    self.notify_client_about_completed_pipeline(file_name)
        except InternalError as err:
            self.notify_client_about_error(err)
        except Exception as err:
            logger.error(err)
            self.notify_client_about_error(err)


if __name__ == "__main__":
    pass
