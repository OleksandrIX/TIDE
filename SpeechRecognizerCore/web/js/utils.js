LOGGER_LEVEL = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARN": "WARN",
    "ERROR": "ERROR",
}

function show_message(message, type) {
    let backgroundColor;
    let icon;

    switch (type) {
        case LOGGER_LEVEL.ERROR:
            icon = '../assets/icons/error.png';
            backgroundColor = "linear-gradient(to right, #FF0000, #FF6347)";
            break;
        case LOGGER_LEVEL.INFO:
            icon = '../assets/icons/info.png';
            backgroundColor = "linear-gradient(to right, #1E90FF, #00BFFF)";
            break;
        case LOGGER_LEVEL.WARN:
            icon = '../assets/icons/warning.png';
            backgroundColor = "linear-gradient(to right, #FFD700, #FFA500)";
            break;
        default:
            backgroundColor = "#FFFFFF";
    }

    Toastify({
        text: `<img src="${icon}" style="width: 20px; height: 20px;" alt="meow"> ${message}`,
        newWindow: true,
        close: true,
        duration: 3000,
        position: 'right top',
        backgroundColor: backgroundColor,
        stopOnFocus: true,
    }).showToast();

}

const loader_container = document.getElementById('loader_container')
const loader = document.createElement('div')
loader.className = 'dot-elastic'

function show_loader() {
    loader_container.appendChild(loader)
    loader_container.classList.add('loader-active')
    loader_container.classList.remove('loader-inactive')
}

function hide_loader() {
    loader_container.removeChild(loader)
    loader_container.classList.remove('loader-active')
    loader_container.classList.add('loader-inactive')
}