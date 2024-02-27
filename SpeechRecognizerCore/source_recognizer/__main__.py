import pyaudio
from source_recognizer import recording, get_device_from_name


def list_input_devices() -> None:
    """
    Lists all input devices available to pyaudio
    :return: None
    """
    py_audio = pyaudio.PyAudio()

    for i in range(py_audio.get_device_count()):
        device_info = py_audio.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            print(f"{i}: {device_info['name']}")

    py_audio.terminate()


def select_input_device() -> int:
    """
    Selects input device from devices available to pyaudio
    :return: int
    """
    list_input_devices()
    return int(input("Select an input device: "))


def recording_start(destination_path: str = "./") -> str:
    """
    Starts recording from selected input device and saves it to destination_path/output_audiofile
    :param destination_path: str
    :return: str, path to output file
    """
    input_device = select_input_device()
    return recording(destination_path, input_device)


if __name__ == "__main__":
    recording("./", get_device_from_name())
