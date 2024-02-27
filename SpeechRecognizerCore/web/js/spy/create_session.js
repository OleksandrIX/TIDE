const session_creat_modal = document.querySelector(".creat-session-modal");

const session_create_btn = document.querySelector(".session-btn.create");
session_create_btn.addEventListener("click", () => {
    session_creat_modal.classList.toggle("open");
});

const close_modal_btn = document.querySelector(".creat-session-modal .close-modal");
close_modal_btn.addEventListener("click", () => {
    session_creat_modal.classList.toggle("open");
});

const creat_session_form = document.querySelector(".creat-session-form");
const creat_btn = creat_session_form.querySelector(".modal-btn.creat-session");
creat_btn.addEventListener("click", async () => {
    const session = {
        "name": creat_session_form["name"].value
    };

    const response = await eel.create_session(session)()

    if (response.status !== 201) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR);
    }

    session_creat_modal.classList.toggle("open");
    await load_sessions();
    show_message(response.body.message, LOGGER_LEVEL.INFO);
});