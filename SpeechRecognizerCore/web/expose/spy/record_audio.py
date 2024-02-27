import eel
import pipeline
import threading
import spy_utils
import asyncio
from queue import Queue
from pathlib import Path
from loguru import logger

from sources.response import Response

DATA_STORE_PATH = Path("./data_store")
SPY_PATH = Path(DATA_STORE_PATH, "spy")

default_language_to_use = None
is_auto_azure_upload = False
is_working_pipeline = False

recording_queue = Queue()
recording_thread = None
recording_logs = None

pipeline_queue = Queue()
pipeline_thread = None
pipeline_obj = None


@eel.expose
def start_listening(session_id,
                    default_language,
                    is_auto_upload,
                    is_enabled_pipeline):
    global default_language_to_use
    default_language_to_use = default_language

    logger.debug(f"Set default language - {default_language}")

    global is_auto_azure_upload
    is_auto_azure_upload = is_auto_upload

    logger.debug(f"Auto Azure uploading - {is_auto_azure_upload}")

    global is_working_pipeline
    is_working_pipeline = is_enabled_pipeline

    logger.debug(f"Pipeline enabling - {is_working_pipeline}")

    global recording_logs
    session_path = Path(SPY_PATH, session_id)
    recording_logs = logger.add(str(Path(session_path, "session.log")), level="INFO")

    if not session_path.exists():
        return Response(status=404,
                        body={"message": f"Directory {session_id} in 'spy' not found"}).to_dict()

    try:
        if is_working_pipeline:
            global pipeline_obj

            if not pipeline_obj:
                pipeline_obj = init_pipeline()
                logger.info("Initialized pipeline thread")

        start_recording(session_path)
        spy_utils.update_session_info(str(session_path), is_active=True)
        logger.info("Listening to the microphone has started")
    except Exception as err:
        logger.error(err)
        spy_utils.update_session_info(str(session_path), is_active=False)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def stop_listening(session_id):
    global recording_logs
    session_path = Path(SPY_PATH, session_id)

    try:
        stop_recording()
        logger.remove(recording_logs)
        spy_utils.update_session_info(str(session_path), is_active=False)
        logger.info("Listening to the microphone has finished")
    except Exception as err:
        logger.error(err)
        return Response(status=500, body={"message": str(err)}).to_dict()


@eel.expose
def notify_client_about_new_file(file):
    eel.added_new_audio(file)


@eel.expose
def notify_client_about_completed_pipeline(filename):
    logger.debug(f"pipeline completed for file {filename}")
    eel.completed_pipeline(filename)()


@eel.expose
def notify_client_about_error(err):
    eel.notify_error(err)


def start_recording(destination_path):
    try:
        global recording_thread, recording_queue, pipeline_obj, pipeline_queue, pipeline_thread
        recording_queue.put(True)

        recording_thread = threading.Thread(
            target=pipeline.record_audio,
            args=(destination_path,
                  recording_queue,
                  pipeline_queue,
                  notify_client_about_new_file,
                  notify_client_about_error)
        )

        recording_thread.start()
        logger.debug("Recording thread started")

        if pipeline_obj:
            pipeline_thread = threading.Thread(target=pipeline_obj.start_pipeline)
            pipeline_thread.start()
            logger.debug(pipeline_thread)
            logger.debug("Pipeline thread started")
        else:
            logger.debug("Pipeline object is not defined")

    except Exception as err:
        raise err


def init_pipeline():
    global recording_queue, pipeline_queue, default_language_to_use, is_auto_azure_upload

    logger.debug(f"Initializing pipeline: default language to use - {default_language_to_use}")

    try:
        return pipeline.Pipeline(notify_client_about_completed_pipeline,
                                 notify_client_about_error,
                                 default_language_to_use,
                                 is_auto_azure_upload,
                                 recording_queue,
                                 pipeline_queue)
    except Exception as err:
        raise err


def stop_recording():
    global recording_queue, pipeline_queue, recording_thread, pipeline_thread
    recording_queue.put(False)

    if recording_thread is not None:
        recording_thread.join()
        logger.debug("Recording thread terminated")
    else:
        logger.debug("Recording thread is not define")

    pipeline_queue.put(False)
    if pipeline_thread is not None:
        pipeline_thread.join()
        logger.debug("Pipeline thread terminated")
    else:
        logger.debug("Pipeline thread is not define")
