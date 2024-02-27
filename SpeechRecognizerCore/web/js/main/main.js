document.addEventListener('DOMContentLoaded', async function () {
    await fill_file_explorer()
})

const file_explorer_div = document.querySelector(`.root .file_explorer`)

/**
 * Method refreshes the file uploader
 * It removes all files from UI, gets data from BE and fill it to UI
 * @returns {Promise<void>}
 */
async function fill_file_explorer() {
    const response = await eel.list_data_store()()

    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR)
    }

    const file_explorer = response.body.file_explorer

    file_explorer_div.innerHTML = get_file_explorer_card(file_explorer, ACCORDION_NAME)
    apply_accordion(ACCORDION_NAME)
}

async function delete_file(directory_name, file_name) {
    if (!confirm("Are you sure to delete this file?")) {
        return
    }

    const response = await eel.delete_file(directory_name, file_name)()
    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR)
    }

    await fill_file_explorer()
}

async function select_file_upload() {
    const res = await eel.get_file(ALLOWED_EXTENSIONS_TO_UPLOAD)()

    const file_name_p = document.querySelector('table .file_name')
    file_name_p.innerHTML = res

    return res
}

async function init_file_upload() {
    const file_name_p = document.querySelector('table .file_name')
    let file_name
    if (!file_name_p.innerHTML) {
        file_name = await select_file_upload()
        if (!file_name) {
            return
        }
    } else {
        file_name = file_name_p.innerHTML
    }

    await eel.upload_file(file_name)()

    await fill_file_explorer()
}