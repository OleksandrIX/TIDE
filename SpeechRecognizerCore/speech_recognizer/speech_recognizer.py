import speech_recognition as sr

from speech_recognizer.config import get_language_name_from_bcp_47

recognizer = sr.Recognizer()


def recognize_google(language: str,
                     audio_data: sr.AudioFile) -> str:
    """
    Legacy. Only for testing
    Now using the default api key is provided by library
    In the future use own key
    language 'en-US', 'en-GB', 'uk-UA' etc. see <https://gist.github.com/typpo/b2b828a35e683b9bf8db91b5404f1bd1>
    """
    return recognizer.recognize_google(language=language,
                                       audio_data=audio_data)


def recognize_google_cloud(language: str,
                           audio_data: sr.AudioFile) -> str:
    """
    Must use Google cloud API key
    :param language: 'en-US', 'en-GB', 'uk-UA' etc. see https://gist.github.com/typpo/b2b828a35e683b9bf8db91b5404f1bd1
    :param audio_data:
    :return:
    """
    credentials_json_path: str = 'google_cloud_credentials.json'
    return recognizer.recognize_google_cloud(audio_data=audio_data,
                                             language=language,
                                             credentials_json=credentials_json_path)


def recognize_whisper(language: str,
                      audio_data: sr.AudioFile) -> str:
    """
    Current way uses another language-identifier
    language 'english', 'ukrainian' etc. see https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
    """
    with audio_data as source:
        audio_data = recognizer.record(source=source)
        return recognizer.recognize_whisper(audio_data=audio_data,
                                            language=language)


def recognize_sphinx(language: str,
                     audio_data: sr.AudioFile) -> str:
    """
    It's also possible to use our own model to recognize text
    see https://github.com/cmusphinx/sphinxtrain

    :param language: 'en-US', 'en-GB', 'uk-UA' etc. see https://gist.github.com/typpo/b2b828a35e683b9bf8db91b5404f1bd1
    :param audio_data:
    :return:
    """
    with audio_data as source:
        audio_data = recognizer.record(source=source)
        return recognizer.recognize_sphinx(audio_data=audio_data,
                                           language=language,
                                           show_all=False)


def recognize(language: str,
              file_path: str) -> str:
    """
    Метод розпізнавааня звуку
    :param language 'en-US', 'en-GB', 'uk-UA' etc.
    :param file_path path to the .wav file with the clear text
    :raise UnknownValueError in case of Recognizer couldn't understand the given audio
    :raise RequestError Couldn't request the remote service
    """

    audio_file: sr.AudioFile = sr.AudioFile(filename_or_fileobject=file_path)
    with audio_file as source:
        audio_data = recognizer.record(source=source)
    try:
        # result: str = recognize_google(language=language,
        #                                audio_data=audio_data)

        # result: str = recognize_google_cloud(language=language,
        #                                      audio_data=audio_data)

        whisper_language = get_language_name_from_bcp_47(language)
        result: str = recognize_whisper(language=whisper_language,
                                        audio_file=audio_data)

        result: str = recognize_sphinx(audio_data=audio_data,
                                       language=language)
        return result
    except sr.exceptions.UnknownValueError as uv:
        print(str(uv))
