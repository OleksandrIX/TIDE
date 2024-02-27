async function check_azure_connection() {
    const response_connections = await eel.is_azure_connected()()

    if (response_connections.status !== 200) {
        return show_message("Failed to connect to Azure", LOGGER_LEVEL.ERROR)
    }

    if (response_connections.body.is_connected) {
        return show_message("Connected", LOGGER_LEVEL.INFO)
    }

    show_message("Failed to connect", LOGGER_LEVEL.ERROR)
}