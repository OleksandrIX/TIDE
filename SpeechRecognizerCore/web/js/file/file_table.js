const file_info_div = document.querySelector('#root #file-info .table')
const diarization_table_div = document.querySelector('#root #file-diarization .table')


export function sort_language_probabilities(language_probabilities) {
    return Object.entries(language_probabilities)
        .sort((a, b) => b[1] - a[1])
        .reduce((obj, [key, value]) => {
            obj[key] = value;
            return obj;
        }, {});

}


/**
 * Methods gets info about file from BE and fills basic info
 * Duration, Size, Name, Path in table
 * It clears all data in table
 * @param folder_name
 * @param file_path
 * @returns {Promise<*>}
 */
export async function show_file_info(folder_name, file_path) {
    const res = await eel.get_audio_file_by_path(folder_name, file_path)()

    const file = res.body.file

    file_info_div.innerHTML = get_file_info_card(file)

    return file
}

export async function show_language_for_diarization_audio(folder_name, file_name, diarization_row) {
    const response = await eel.get_prediction_language_for_file(folder_name, file_name)()

    if (response.status !== 200 && response.status !== 404) {
        const message = `Failed to get predicted langauge json file - ${response.body.message}`
        append_logs(message, LOGGER_LEVEL.ERROR)
        return show_message(message, LOGGER_LEVEL.ERROR)
    }

    const predicted_language = response.body.file
    if (predicted_language) {
        predicted_language.language_probabilities = sort_language_probabilities(predicted_language.language_probabilities)
    }
    if (diarization_row)
        diarization_row.querySelector(".diarization_language").innerHTML = await get_language_table_card(predicted_language)
}


export async function show_diarization_in_table(folder_name, file_name) {
    const response = await eel.get_diarization_file_by_path(folder_name, file_name)()
    if (response.status !== 200 && response.status !== 404) {
        const message = `Failed to get diarization file - ${response.body.message}`
        append_logs(message, LOGGER_LEVEL.ERROR)
        return show_message(message, LOGGER_LEVEL.ERROR)
    }

    const diarization_data = response.body
    diarization_table_div.innerHTML = await get_diarization_table_card(folder_name, diarization_data)

    if (response.status !== 404) {
        for (let audio of diarization_data.file.diarization_audio_files) {
            const diarization_row = document.getElementById(audio);
            await show_language_for_diarization_audio(folder_name, audio, diarization_row)
        }
    }
}

export async function show_diarization_speech_in_table(folder_name, file_name) {
    file_name = get_file_from_table()
    const response = await eel.get_speech_part_for_file(folder_name, file_name)()

    if (response.status !== 200 && response.status !== 404) {
        const message = response.body.message
        append_logs(message, LOGGER_LEVEL.ERROR)
        return show_message(message, LOGGER_LEVEL.ERROR)
    }

    const speeches = response.body.speeches

    const html_elements = document.getElementsByClassName('diarization-speech-cell')
    for (const i in speeches) {
        const html_element = html_elements[i]
        html_element.innerHTML = speeches[i]
    }
}