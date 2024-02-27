import {load_diarization_to_page} from "./file_spectrogram.js";
import {
    show_diarization_in_table,
    sort_language_probabilities
} from "./file_table.js";


const min_speaker_diarization = document.querySelector('.min_speakers')
min_speaker_diarization.addEventListener('change', check_min_max)

const max_speaker_diarization = document.querySelector('.max_speakers')
max_speaker_diarization.addEventListener('change', check_min_max)

function check_min_max() {
    const minValue = parseInt(document.querySelector('.min_speakers').value);
    const maxValue = parseInt(document.querySelector('.max_speakers').value);

    if (minValue > maxValue) {
        document.querySelector('.min_speakers').value = document.querySelector('.max_speakers').value;
    }
}

export async function denoise(folder_name, file_path) {
    append_logs("Starting denoise the audio", LOGGER_LEVEL.INFO)
    show_loader()

    const response = await eel.denoise_audio(folder_name, file_path)()

    if (response.status !== 200) {
        show_message(response.body.message, LOGGER_LEVEL.ERROR)
        hide_loader()

        return append_logs(`Stops denoise audio - ${response.body.message}`, LOGGER_LEVEL.ERROR)
    }

    const denoise_file_name = response.body.file_name
    location.href = `file.html?file_path=${denoise_file_name}&folder_name=${folder_name}`;

    hide_loader()
    show_message('Successfully completed denoise', LOGGER_LEVEL.INFO)
    append_logs("Audio denoise has finished", LOGGER_LEVEL.INFO)
}

export async function define_language(folder_name, file_path) {
    append_logs("Starting define language", LOGGER_LEVEL.INFO)
    show_loader()

    const language_to_use_select = document.querySelector('.language-to-use-select');
    const language_to_use = language_to_use_select.value;

    const diarization_table = document.querySelector("#diarization-table");
    const diarization_unknown = diarization_table.children[0].querySelector("#diarization-unknown");
    if (diarization_unknown) {
        show_message("Firstly execute diarization", LOGGER_LEVEL.WARN);
        hide_loader()
        return append_logs("Stopping define language - execute diarization at first", LOGGER_LEVEL.WARN);
    }

    if (language_to_use === "AUTO") {
        const response = await eel.define_language(folder_name, file_path)()

        if (response.status !== 200) {
            append_logs(response.body.message, "ERROR")
            hide_loader()
            return append_logs(`Failed to define language - ${response.body.message}`)
        }

        const audio_files = response.body;

        for (let audio_file of audio_files) {
            const diarization_audio_row = document.getElementById(audio_file.file_name);

            let predicted_language = {
                "language_probabilities": audio_file.all_predictions,
                "language": audio_file.max_probability,
                "language_tags": audio_file.language_tags
            }

            if (predicted_language) {
                predicted_language.language_probabilities = sort_language_probabilities(predicted_language.language_probabilities)
            }

            if (diarization_audio_row)
                diarization_audio_row.querySelector(".diarization_language").innerHTML =
                    await get_language_table_card(predicted_language)
        }

        show_message('Successfully completed define language', LOGGER_LEVEL.INFO)
        append_logs(`Language has defined`, LOGGER_LEVEL.INFO)
    } else {
        hide_loader()
        return show_message(`Selected ${language_to_use}`, LOGGER_LEVEL.INFO);
    }

    hide_loader()
    show_message('Successfully completed define language', LOGGER_LEVEL.INFO)
    append_logs(`Language has defined`, LOGGER_LEVEL.INFO)
}

export async function upload_to_azure() {
    append_logs("Starting uploading to Azure", LOGGER_LEVEL.INFO)
    show_loader()

    const folder_name = get_param_from_url("folder_name", window.location.href)
    const response = await eel.upload_folder_to_azure(folder_name)()
    if (response.status !== 200) {
        show_message(response.body.message, LOGGER_LEVEL.WARN)
    }

    hide_loader()
    show_message('Successfully completed upload to azure', LOGGER_LEVEL.INFO)
    append_logs("Uploading to Azure has finished", LOGGER_LEVEL.INFO)
}

export async function diarization(folder_name, file_name) {
    append_logs("Starting diarization the audio", LOGGER_LEVEL.INFO)
    show_loader()

    const response = await eel.diarization_audio(folder_name, file_name, min_speaker_diarization.value, max_speaker_diarization.value)()

    if (response.status !== 200) {
        show_message(response.body.message, LOGGER_LEVEL.ERROR)
        hide_loader()
        return append_logs(`Stops diarization audio - ${response.body.message}`, LOGGER_LEVEL.ERROR)
    }

    await load_diarization_to_page(folder_name, file_name)
    await show_diarization_in_table(folder_name, file_name)

    hide_loader()
    show_message('Successfully completed diarization', LOGGER_LEVEL.INFO)
    append_logs("Audio diarization has finished", LOGGER_LEVEL.INFO)

    // await recognize_text_for_diarization(folder_name, file_name)
}

export async function recognize_text_for_diarization(folder_name, file_name) {
    append_logs("Starting recognize text for parts diarized data", LOGGER_LEVEL.INFO)
    show_loader()

    const language_to_use_select = document.querySelector('.language-to-use-select')
    const language_to_use = language_to_use_select.value

    let tags = []

    if (language_to_use === "AUTO") {
        const language_tag_th = document.querySelector(`#language_tags_th`)

        if (!language_tag_th || language_tag_th.innerHTML === "UNKNOWN") {
            show_message("Firstly define language", LOGGER_LEVEL.WARN)
            hide_loader()
            return append_logs("Stops recognize text for parts diarized data - define language at first", LOGGER_LEVEL.WARN)
        }
    }

    tags = [language_to_use]

    const response = await eel.get_speeches_for_diarized_data(tags, folder_name, file_name)()

    if (response.status !== 200) {
        const message = response.body.message
        show_message(message, LOGGER_LEVEL.ERROR)
        hide_loader()
        return append_logs(message, LOGGER_LEVEL.ERROR)
    }

    const speeches = response.body.speeches

    const html_elements_for_diarized_speech = document.getElementsByClassName('diarization-speech-cell')
    for (const i in speeches) {
        const html_element = html_elements_for_diarized_speech[i]
        html_element.innerHTML = speeches[i]
    }

    hide_loader()
    show_message('Successfully completed recognize speach for diarization', LOGGER_LEVEL.INFO)
    append_logs("Speech recognitions for diarized data was finished", LOGGER_LEVEL.INFO)
}

export async function start_pipeline(folder_name, file_name) {
    append_logs("Starting pipeline for audio file", LOGGER_LEVEL.INFO);
    show_loader()

    await diarization(folder_name, file_name);
    await define_language(folder_name, file_name);
    await recognize_text_for_diarization(folder_name, file_name);

    hide_loader()
    show_message("Successfully completed pipeline", LOGGER_LEVEL.INFO);
    append_logs("Pipeline for audio file was finished", LOGGER_LEVEL.INFO);
}