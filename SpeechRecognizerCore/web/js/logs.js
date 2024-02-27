const logs = []
const logs_container = document.getElementById("logs_container")
const filter_panel = document.getElementById("filter_panel")

const LOG_TYPES = {
    TRACE: "TRACE",
    DEBUG: "DEBUG",
    INFO: "INFO",
    SUCCESS: "SUCCESS",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL"
}

const filter = {
    types: [],
    date: {}
}

const LOG_COLORS = {
    [LOG_TYPES.TRACE]: '#808080',
    [LOG_TYPES.DEBUG]: '#0000FF',
    [LOG_TYPES.INFO]: '#008000',
    [LOG_TYPES.SUCCESS]: '#00FF00',
    [LOG_TYPES.WARNING]: '#FFA500',
    [LOG_TYPES.ERROR]: '#FF0000',
    [LOG_TYPES.CRITICAL]: '#800000'
};

document.addEventListener('DOMContentLoaded', async function () {
    filter.types = Object.values(LOG_TYPES)
    create_filter_panel()
    schedule_logs()
})

function create_filter_panel() {
    const types_row = document.createElement("div")
    types_row.classList.add("filter_panel_row")
    filter.types.forEach(x => {
        const div = document.createElement("label")
        div.classList.add("checkbox_item")
        div.textContent = x

        const checkbox = document.createElement("input")
        checkbox.type = "checkbox"
        checkbox.checked = true

        checkbox.addEventListener("change", (event) => {
            if (event.target.checked) {
                filter.types.push(x)
            } else {
                filter.types = filter.types.filter(y => y != x)
            }
            filter_update()
        })

        div.append(checkbox)
        types_row.append(div)
    })

    filter_panel.append(types_row)

    const date_row = document.createElement("div")
    date_row.classList.add("filter_panel_row")

    const to_input = document.createElement("input")
    to_input.type = "datetime-local"

    const from_input = document.createElement("input")
    from_input.type = "datetime-local"

    from_input.addEventListener("change", (event) => {
        if (event.target.value) {
            filter.date.from = new Date(event.target.value)
        } else {
            delete filter.date.from
        }
        filter_update()
    })

    to_input.addEventListener("change", (event) => {
        if (event.target.value) {
            filter.date.to = new Date(event.target.value)
        } else {
            delete filter.date.to
        }
        filter_update()
    })

    date_row.append(from_input)

    date_row.append(to_input)

    filter_panel.append(date_row)
}

function schedule_logs() {
    setInterval(async () => {
        let new_logs = await eel.get_logs()()
        let last_log_date;

        if (logs.length > 0) {
            last_log_date = logs[logs.length - 1].date
        }

        let new_obj_logs = new_logs.map(x => {
            let obj = transform_string_log_obj(x)
            if (last_log_date) {
                if (last_log_date < obj.date) {
                    return obj
                }
            } else {
                return obj
            }
        })

        new_logs = new_obj_logs.filter(x => x)
        append_logs(new_logs)
        logs.push(...new_logs)
    }, 1_000)
}

function filter_update() {
    logs_container.innerHTML = ""
    append_logs(logs)
}

function append_logs(new_logs) {
    new_logs.forEach(log => {
        const item = document.createElement("div")
        item.classList.add("log_item")

        if (!filter.types.includes(LOG_TYPES[log.type])) {
            item.classList.add("hidden")
        }

        if (filter.date.from) {
            console.log(filter.date.from);
            if (filter.date.from.getTime() > log.date.getTime()) {
                item.classList.add("hidden")
            }
        }

        if (filter.date.to) {
            if (filter.date.to.getTime() < log.date.getTime()) {
                item.classList.add("hidden")
            }
        }

        const item_date = document.createElement("div")
        item_date.classList.add("log_item_date")
        item_date.textContent = formate_date(log.date)

        const item_type = document.createElement("div")
        item_type.classList.add("log_item_type")
        item_type.textContent = log.type
        item_type.style.color = LOG_COLORS[LOG_TYPES[log.type]]

        const item_message = document.createElement("div")
        item_message.textContent = log.message

        item.append(item_date)
        item.append(item_type)
        item.append(item_message)

        logs_container.append(item)
    });
}

function formate_date(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // January is 0!
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${day}:${month}:${year} ${hours}:${minutes}:${seconds}`;
}

function transform_string_log_obj(log) {
    let obj = {}
    let splited_log = log.split("|")
    obj.date = new Date(splited_log[0].trim())
    obj.type = splited_log[1].trim()
    obj.message = splited_log[2].trim()
    return obj
}