import os
import wave
import asyncio
import eel
import numpy as np
import pyaudio
from queue import Queue
from pathlib import Path
from loguru import logger
from datetime import datetime

from pydub import AudioSegment
from pydub.silence import split_on_silence

from source_recognizer.settings import get_settings
from exceptions.InternalError import InternalError


def create_folder_structure_audio(path_to_folder):
    if not Path(path_to_folder).exists():
        os.mkdir(path_to_folder)

    sub_folders = ["diarization", "language", "speech"]
    for sub_folder in sub_folders:
        path_to_sub_folder = Path(path_to_folder, sub_folder)
        if not path_to_sub_folder.exists():
            os.mkdir(path_to_sub_folder)


class Recording:
    def __init__(self,
                 format_audio: pyaudio = pyaudio.paInt16,
                 chunk: int = 1024) -> None:
        self.format_audio: pyaudio = format_audio
        self.chunk: int = chunk

        settings = get_settings()
        self.device: int = settings["microphone"]
        self.channels: int = settings["channels"]
        self.rate: int = settings["sample_rate"]
        self.voice_threshold = settings["voice_threshold"]
        self.voice_end_delay = settings["voice_end_delay"]

    def is_voice(self, sample):
        return np.max(sample) > self.voice_threshold

    def start_recording(self, destination_path: str,
                        recording_queue: Queue,
                        pipeline_queue: Queue,
                        notify_client_about_new_file,
                        notify_client_about_error):
        recording = False
        start_time = None
        stream = None
        py_audio = pyaudio.PyAudio()

        try:
            stream = py_audio.open(format=self.format_audio,
                                   channels=self.channels,
                                   rate=self.rate,
                                   input=True,
                                   input_device_index=self.device,
                                   frames_per_buffer=self.chunk)

            frames = []
            while True:
                data = stream.read(self.chunk)
                frames.append(data)

                audio_segment = AudioSegment(data=data,
                                             sample_width=2,
                                             frame_rate=self.rate,
                                             channels=self.channels)
                voice = audio_segment.dBFS != float('-inf')

                if voice and not recording:
                    frames.clear()
                    recording = True
                    start_time = datetime.now()
                    logger.info("Recording started")
                elif not voice and recording:
                    if (datetime.now() - start_time).seconds >= self.voice_end_delay:
                        folder_name = f"record_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
                        file_name = f"{folder_name}.wav"
                        path_to_folder = Path(destination_path, folder_name)
                        path_to_audio = Path(path_to_folder, file_name).absolute()

                        create_folder_structure_audio(path_to_folder)

                        audio = AudioSegment(data=b''.join(frames),
                                             sample_width=2,
                                             frame_rate=self.rate,
                                             channels=self.channels)

                        audio.export(path_to_audio, format="wav")
                        logger.info(f"Recording saved to {path_to_audio}")

                        notify_client_about_new_file(os.path.basename(path_to_audio))
                        frames = []
                        recording = False
                        pipeline_queue.put(path_to_audio)
                if not recording_queue.empty():
                    is_recording = recording_queue.get()
                    if not is_recording:
                        break
        except OSError as err:
            logger.error(err)
            notify_client_about_error("This microphone is not suitable for audio recording")
        except InternalError as err:
            logger.error(err)
            notify_client_about_error(err)
        except Exception as err:
            logger.error(err)
            notify_client_about_error(err)
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            py_audio.terminate()
