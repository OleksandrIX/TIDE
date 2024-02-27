from denoise import denoise

if __name__ == "__main__":
    sample_rate = 8000
    frame_length = 8064
    hop_length_frame = 8064
    n_fft = 255
    hop_length_fft = 63
    model_weights_path = "./weights/model_unet.h5"
    model_architecture_path = "./weights/model_unet.json"
    volume = 40

    denoise(model_weights_path=model_weights_path,
            model_architecture_path=model_architecture_path,
            audio_input_noise="1.wav",
            audio_output_prediction="./audio_clean/test_8k.wav",
            sample_rate=sample_rate,
            frame_length=frame_length,
            hop_length_frame=hop_length_frame,
            n_fft=n_fft,
            hop_length_fft=hop_length_fft,
            volume=volume)
