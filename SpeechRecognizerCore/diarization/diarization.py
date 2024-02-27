from loguru import logger
from pydub import AudioSegment
import torch


def diarization(audio_input_path, pipeline, audio_output_path, min_diarization_speakers, max_diarization_speakers):
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    logger.info("Starting diarization")
    diarization_speakers = pipeline(audio_input_path,
                                    min_speakers=1 if min_diarization_speakers == 'AUTO'
                                    else int(min_diarization_speakers),
                                    max_speakers=1 if max_diarization_speakers == 'AUTO'
                                    else int(max_diarization_speakers))

    audio = AudioSegment.from_file(audio_input_path)

    with open(audio_output_path, "w") as rttm:
        for turn, _, speaker in diarization_speakers.itertracks(yield_label=True):
            speaker = speaker.split("_")[1]
            rttm.write(f"{turn.start:.3f} {turn.end:.3f} #{speaker}\n")

            speaker_audio = audio[int(turn.start * 1000):int(turn.end * 1000)]
            output_file_path = f"{audio_output_path}_{turn.start:.3f}_{turn.end:.3f}_#{speaker}.wav"
            speaker_audio.export(output_file_path, format="wav")

    logger.info("Finished diarization")
