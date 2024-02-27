const session_id = get_param_from_url("session_id", window.location.href);
const session_info = document.querySelector(".session-header>.session-info");
const session_body = document.querySelector(".session-body");

const start_btn = document.querySelector(".session-control .start");
const pause_btn = document.querySelector(".session-control .pause");

document.addEventListener("DOMContentLoaded", async () => {
    const {session, audio_files, groups} = await get_session(session_id);
    render_session_info(session, audio_files);
    render_session_files(groups);
    set_active_control(session.is_active);
    await fill_default_language_to_use()
});

async function get_session(session_id) {
    const response = await eel.get_session_by_id(session_id)();

    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR);
    }

    const session = response.body.session;
    const audio_files = response.body.audio_files;
    const groups = response.body.groups;
    return {session, audio_files, groups};
}

function render_session_info(session, audio_files) {
    session_info.querySelector(".session-id>span").textContent = session_id;
    session_info.querySelector(".session-name>span").textContent = session.name;
    session_info.querySelector(".session-audio-files>span").textContent = audio_files.length;
    session_info.querySelector(".created-at>span").textContent = session.created_at;
}

function toggle_active_btn() {
    start_btn.classList.toggle("active");
    pause_btn.classList.toggle("active");
}

function set_active_control(is_active) {
    if (is_active) {
        pause_btn.classList.add("active");
    } else {
        start_btn.classList.add("active");
    }

    start_btn.addEventListener("click", toggle_active_btn);
    pause_btn.addEventListener("click", toggle_active_btn);

}

async function delete_file_handler(event, folder_name, file_name) {
    event.stopPropagation();

    const response = await eel.delete_file(folder_name, file_name)()
    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR)
    }

    get_session(session_id).then(({session, audio_files, groups}) => {
        render_session_info(session, audio_files);
        render_session_files(groups);
        append_logs(`Removed audio file: ${file_name}`, LOGGER_LEVEL.INFO)
    });
}

function render_session_files(groups) {
    const files_container = session_body.querySelector(".files");
    files_container.innerHTML = "";

    if (Object.keys(groups).length === 0) {
        const empty_groups_block = document.createElement("div");
        empty_groups_block.classList.add("empty-groups");
        empty_groups_block.textContent = "No audio files in this session";
        files_container.appendChild(empty_groups_block);
        return;
    }

    for (let name_group in groups) {
        const accordion_header_data = `
            <p><b>Airwave:</b> ${name_group} <br> <b>Duration: </b>${(groups[name_group][0].duration)}s.</br></p>
        `;

        let accordion_content_data = ``;

        for (let audio of groups[name_group]) {
            let folder_name = `spy%2F${session_id}%2F${name_group}`;

            accordion_content_data += `
                <p>
                    <a class="file-link"
                       href="file.html?file_path=${audio.filename}&folder_name=${folder_name}">
                        ${audio.filename}
                    </a>
                    <span class="delete-audio-btn" onclick="delete_file_handler(event, '${folder_name}', '${audio.filename}')">x</span>
                </p>
            `;
        }

        const group_audio_container = create_accordion_element(
            "group-audio-files",
            accordion_header_data,
            accordion_content_data
        );

        group_audio_container.addEventListener("click", () => {
            group_audio_container.querySelector(".accordion-header>.accordion-trigger.arrow-up").classList.toggle("active");
            group_audio_container.querySelector(".accordion-header>.accordion-trigger.arrow-down").classList.toggle("active");
            group_audio_container.querySelector(".accordion-content").classList.toggle("active");
        });

        files_container.appendChild(group_audio_container);
    }
}

async function fill_default_language_to_use() {
    const spy_language_to_use_select = document.querySelector(`#spy_language_to_use_div select`)
    const manual_languages = await eel.get_manual_language()()
    spy_language_to_use_select.innerHTML += `<option value="AUTO">AUTO</option>`
    for (const language of manual_languages) {
        spy_language_to_use_select.innerHTML += `<option value="${language}">${language}</option>`
    }
}
