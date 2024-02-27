import noisereduce as nr
import numpy as np
import soundfile as sf
from loguru import logger
from pydub import AudioSegment

from denoise.data_tools import (numpy_audio_to_matrix_spectrogram,
                                matrix_spectrogram_to_numpy_audio)
from denoise.data_tools import scaled_in, inv_scaled_ou, audio_to_numpy


def denoise(loaded_model,
            audio_output_prediction,
            sample_rate,
            frame_length,
            hop_length_frame,
            n_fft,
            hop_length_fft,
            audio_input_noise,
            volume,
            is_model,
            is_spectral_gating):
    if is_model and is_spectral_gating:
        denoise_via_model(loaded_model,
                          audio_output_prediction,
                          sample_rate,
                          frame_length,
                          hop_length_frame,
                          n_fft,
                          hop_length_fft,
                          audio_input_noise,
                          volume)

        denoise_via_noise_reduce(audio_output_prediction, audio_output_prediction, volume)
        return

    if is_model:
        denoise_via_model(loaded_model,
                          audio_output_prediction,
                          sample_rate,
                          frame_length,
                          hop_length_frame,
                          n_fft,
                          hop_length_fft,
                          audio_input_noise,
                          volume)
    if is_spectral_gating:
        denoise_via_noise_reduce(audio_input_noise,
                                 audio_output_prediction, volume)


def denoise_via_model(loaded_model,
                      audio_output_prediction,
                      sample_rate,
                      frame_length,
                      hop_length_frame,
                      n_fft,
                      hop_length_fft,
                      audio_input_noise, volume):
    logger.info("Starting denoise via model")
    audio = audio_to_numpy(sample_rate, frame_length, hop_length_frame, audio_input_noise)

    dim_square_spec = int(n_fft / 2) + 1
    m_amp_db_audio, m_pha_audio = numpy_audio_to_matrix_spectrogram(
        audio, dim_square_spec, n_fft, hop_length_fft)

    X_in = scaled_in(m_amp_db_audio)
    X_in = X_in.reshape(X_in.shape[0], X_in.shape[1], X_in.shape[2], 1)
    X_pred = loaded_model.predict(X_in)
    inv_sca_X_pred = inv_scaled_ou(X_pred)
    X_denoise = m_amp_db_audio - inv_sca_X_pred[:, :, :, 0]

    audio_denoise_recons = matrix_spectrogram_to_numpy_audio(X_denoise, m_pha_audio, frame_length, hop_length_fft)
    nb_samples = audio_denoise_recons.shape[0]
    denoise_long = audio_denoise_recons.reshape(1, nb_samples * frame_length) * volume  # Гучність аудіо після денойзу

    sf.write(audio_output_prediction, denoise_long[0, :], sample_rate, 'PCM_24')

    logger.info("Finishing denoise via model")


def denoise_via_noise_reduce(audio_input_noise, audio_output_clean, volume):
    logger.info("Starting denoise via spectral gating")
    audio = AudioSegment.from_file(audio_input_noise)

    samples = np.array(audio.get_array_of_samples())

    reduced_noise = nr.reduce_noise(samples, sr=audio.frame_rate)

    reduced_audio = AudioSegment(
        reduced_noise.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=audio.sample_width,
        channels=audio.channels
    )

    reduced_audio = reduced_audio + volume

    reduced_audio.export(audio_output_clean, format="wav")
    logger.info("Finishing denoise via spectral gating")
