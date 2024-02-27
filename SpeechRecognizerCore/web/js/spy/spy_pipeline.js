async function start_listening() {
    append_logs("Start listening", LOGGER_LEVEL.INFO);
    localStorage.setItem("session_id", session_id)
    show_loader()

    const spy_language_to_use_select = document.querySelector(`#spy_language_to_use_div select`)
    const is_auto_upload = document.querySelector('#spy_auto_azure_uploading label input')
    const is_enable_pipeline = document.querySelector("#spy_control_pipeline input")

    const response = await eel.start_listening(session_id,
        spy_language_to_use_select.value,
        is_auto_upload.checked,
        is_enable_pipeline.checked)()

    if (response?.status && response.status !== 200) {
        toggle_active_btn()
        return show_message(response.body.message, LOGGER_LEVEL.ERROR);
    }

    hide_loader()
    append_logs("Start listening", LOGGER_LEVEL.INFO);
}

async function stop_listening() {
    append_logs("Stop listening", LOGGER_LEVEL.INFO);
    localStorage.removeItem("session_id")
    const response = await eel.stop_listening(session_id)()
    if (response?.status && response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR);
    }

    append_logs("Stop listening", LOGGER_LEVEL.INFO);
}

eel.expose(added_new_audio)

function added_new_audio(file) {
    get_session(session_id).then(({session, audio_files, groups}) => {
        render_session_info(session, audio_files);
        render_session_files(groups);
        append_logs(`Recorded new audio: ${file}`, LOGGER_LEVEL.INFO)
    });
}

eel.expose(completed_pipeline)

function completed_pipeline(filename) {
    get_session(session_id).then(({session, audio_files, groups}) => {
        render_session_info(session, audio_files);
        render_session_files(groups);
        append_logs(`Pipeline completed for ${filename}`, LOGGER_LEVEL.DEBUG);
    });
}

eel.expose(notify_error)

function notify_error(err) {
    show_message(err, LOGGER_LEVEL.ERROR);
}
