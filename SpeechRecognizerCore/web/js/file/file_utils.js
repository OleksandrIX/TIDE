function get_param_from_url(param_name, url) {
    const urlParams = new URL(url);
    return urlParams.searchParams.get(param_name);
}

function get_file_from_table() {
    const abs_path = document.querySelector('#file_path_th').innerHTML

    // Check Linux
    let path_parts = abs_path.split('/')
    if (path_parts.length !== 1) {
        return path_parts[path_parts.length - 1]
    }
    // Check Windows
    path_parts = abs_path.split('\\')
    if (path_parts.length !== 1) {
        return path_parts[path_parts.length - 1]
    }

    throw "Unknown file system"
}

function get_folder_from_table() {
    const abs_path = document.querySelector('#file_path_th').innerHTML

    // Check Linux
    let path_parts = abs_path.split('/')
    if (path_parts.length !== 1) {
        return path_parts[path_parts.length - 2]
    }
    // Check Windows
    path_parts = abs_path.split('\\')
    if (path_parts.length !== 1) {
        return path_parts[path_parts.length - 2]
    }

    throw "Unknown file system"
}

/**
 * Returns image data
 * @param folder_name
 * @param file_name
 */
async function get_language_image_of_file(folder_name, file_name) {
    const response = await eel.get_language_image_file_data(folder_name, file_name, "language")()

    if (response.status !== 200) {
        const message = "Failed to get language image - " + response.body.message
        append_logs(message)
        return show_message(message, LOGGER_LEVEL.ERROR)
    }

    return response.body.data
}

async function get_audio_diarization_data(folder_name, file_name) {
    const response = await eel.get_diarization_audio(folder_name, file_name)()

    if (response.status !== 200) {
        const message = "Failed to get diarization audio - " + response.body.message
        append_logs(message, LOGGER_LEVEL.ERROR)
        return show_message(message, LOGGER_LEVEL.ERROR)
    }

    return response.body
}

