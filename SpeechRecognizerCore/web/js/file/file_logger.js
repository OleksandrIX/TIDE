const logs_textarea = document.querySelector(`.logs textarea`)
clear_logs()

function append_logs(line, level) {
    const log = level.toUpperCase() + " | " + new Date().toISOString() + " | " + line + "\n"
    logs_textarea.value += log
}

function clear_logs() {
    logs_textarea.value = ""
}
