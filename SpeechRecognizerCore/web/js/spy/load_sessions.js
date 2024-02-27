const sessions_container = document.querySelector(".sessions-container");
const amount_sessions = document.querySelector(".sessions-header h2 span")


document.addEventListener("DOMContentLoaded", async () => {
    await load_sessions();
});

async function load_sessions() {
    sessions_container.innerHTML = "";
    const response = await eel.list_sessions_in_spy()();

    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR);
    }

    const sessions = response.body.sessions;

    if (sessions.length === 0) {
        const empty_block = document.createElement("div");
        empty_block.classList.add("empty-session");
        empty_block.textContent = "Spy sessions empty"
        sessions_container.appendChild(empty_block);
    }

    amount_sessions.textContent = sessions.length;

    for (let session of sessions) {
        const accordion_header_data = `
            <p><b>Session name:</b> <span>${session.info.name}</span></p>
        `;

        const accordion_content_data = `
            <p>Session id: <span>${session.session_id}</span></p>
            <p>Created at: <span>${session.info.created_at}</span></p>
            <p>Total audios: <span>${session.audio_files.length}</span></p>
            <p>${session.info.is_active ? "Session is running" : "Session is not running"}</p>            
            <div class="delete-btn-wrapper">
                <img class="delete-btn" src="./assets/icons/delete.svg" alt="delete">
            </div>
        `;

        const session_element = create_accordion_element(
            "session-wrapper",
            accordion_header_data,
            accordion_content_data
        );

        session_element.addEventListener("click", (e) => {
            window.location.href = `session.html?session_id=${session.session_id}`
        });

        session_element
            .querySelector(".delete-btn-wrapper")
            .addEventListener("click", async (e) => {
                e.stopPropagation();
                await eel.delete_session(session.session_id)();
                await load_sessions();
            });

        sessions_container.appendChild(session_element);
    }
}