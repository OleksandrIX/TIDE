let blocks = []
const root = this.document.getElementById("settings_form");

const BLOCK_PREFIX = "_id_block"
const LIST_PREFIX = "_id_list"

const ITEM_TYPES = {
    TEXT: "text",
    NUMBER: "number",
    PASSWORD: "password",
    BUTTON: "button",
    TOGGLER: "toggler",
    TOGGLER_BETWEEN: "toggler-between",
    FILE: "file",
    DOUBLE_CB_LIST: "double-cb-list",
    DOUBLE_INPUT_LIST: "double-input-list",
    SELECT: "select",
    LIST_DIRS: "list-dirs"
};

const data_validate_functions = {
    [ITEM_TYPES.SELECT]: validate_select_data,
    [ITEM_TYPES.TEXT]: validate_input_data,
    [ITEM_TYPES.NUMBER]: validate_input_data,
    [ITEM_TYPES.PASSWORD]: validate_input_data,
    [ITEM_TYPES.FILE]: validate_file_data,
    [ITEM_TYPES.DOUBLE_CB_LIST]: validate_double_cb_list_data,
    [ITEM_TYPES.DOUBLE_INPUT_LIST]: validate_double_input_list_data,
    [ITEM_TYPES.LIST_DIRS]: validate_list_dir_data,
}

const data_set_functions = {
    [ITEM_TYPES.SELECT]: set_select_data,
    [ITEM_TYPES.TEXT]: set_input_data,
    [ITEM_TYPES.NUMBER]: set_input_data,
    [ITEM_TYPES.PASSWORD]: set_input_data,
    [ITEM_TYPES.TOGGLER_BETWEEN]: set_toggler_between_data,
    [ITEM_TYPES.FILE]: set_file_data,
    [ITEM_TYPES.TOGGLER]: set_toggler_data,
}

const data_retrieval_functions = {
    [ITEM_TYPES.SELECT]: get_select_data,
    [ITEM_TYPES.TEXT]: get_input_data,
    [ITEM_TYPES.NUMBER]: get_input_data,
    [ITEM_TYPES.PASSWORD]: get_input_data,
    [ITEM_TYPES.TOGGLER_BETWEEN]: get_toggler_between_data,
    [ITEM_TYPES.FILE]: get_file_data,
    [ITEM_TYPES.DOUBLE_CB_LIST]: get_double_cb_list_data,
    [ITEM_TYPES.DOUBLE_INPUT_LIST]: get_double_input_list_data,
    [ITEM_TYPES.LIST_DIRS]: get_list_dir_data,
    [ITEM_TYPES.TOGGLER]: get_toggler_data,
};

const itemTypeToFunctionMap = {
    [ITEM_TYPES.TEXT]: add_input,
    [ITEM_TYPES.NUMBER]: add_input,
    [ITEM_TYPES.PASSWORD]: add_input,
    [ITEM_TYPES.BUTTON]: add_button,
    [ITEM_TYPES.TOGGLER]: add_toggler,
    [ITEM_TYPES.TOGGLER_BETWEEN]: add_toggler_between,
    [ITEM_TYPES.FILE]: add_file_input,
    [ITEM_TYPES.DOUBLE_CB_LIST]: add_double_cb_list,
    [ITEM_TYPES.DOUBLE_INPUT_LIST]: add_double_input_list,
    [ITEM_TYPES.SELECT]: add_select,
    [ITEM_TYPES.LIST_DIRS]: add_list_dirs
};

const BUTTON_ON_CLICK_EVENTS = {
    "AZURE_TEST_CONNECTION": async () => {
        await check_azure_connection()
    },
}

document.addEventListener('DOMContentLoaded', async function () {
    blocks = JSON.parse(await eel.get_ui_default_settings()())
    let user_settings;

    try {
        user_settings = JSON.parse(await eel.get_settings()())
    } catch {
        show_message("Can't load user settings", LOGGER_LEVEL.ERROR);
    }


    if (user_settings) {
        blocks.forEach(x => {
            const user_block = user_settings[x.id];

            if (user_block) {
                Object.keys(user_block).forEach(async (key) => {
                    const item = x.items.filter(i => i.id === key)[0]

                    if (ITEM_TYPES.SELECT === item.type) {
                        if (item.id === "microphone") {
                            item.options = await eel.get_microphones()()
                            if (item.options.length != 0) {
                                const selected = item.options.find(x => x.index === user_block[key])
                                if (selected) {
                                    item.selected = selected.value
                                }
                            }
                        } else {
                            item.selected = user_block[key]
                        }
                    }

                    if (ITEM_TYPES.TEXT === item.type || ITEM_TYPES.NUMBER === item.type || ITEM_TYPES.PASSWORD === item.type) {
                        item.value = user_block[key]
                    }

                    if (ITEM_TYPES.TOGGLER_BETWEEN === item.type) {
                        item.value = user_block[key][`is_${item.items[1].id}`];

                        if (item.value) {
                            item.items[1].value = user_block[key][`${item.items[1].id}`]
                        } else {
                            item.items[0].value = user_block[key][`${item.items[0].id}`]
                        }
                    }

                    if (ITEM_TYPES.FILE === item.type) {
                        item.value = user_block[key];
                    }

                    if (ITEM_TYPES.DOUBLE_INPUT_LIST === item.type) {
                        item.items = user_block[key]
                    }

                    if (ITEM_TYPES.TOGGLER === item.type) {
                        item.value = user_block[key]
                    }
                })
            }
        })
    }

    await prepare_data()

    run()
});

function validate_data(item) {
    if (item.require) {
        const data_validate_function = data_validate_functions[item.type]

        if (data_validate_function) {
            return data_validate_function(item)
        }
    }

    return true
}

function get_toggler_data(item) {
    const toggler = document.getElementById(item.id)
    const value = toggler.checked
    return { [item.id]: value }
}

function set_toggler_data(item, value) {
    item.value = value
}

function get_double_cb_list_data(item) {
    validate_data(item)

    let value = item.items.filter(x => x.selected).map(x => {
        if (x.selected) {
            return { [x.value]: x.items.filter(i => i.selected).map(i => i.value) }
        }
    })

    value = Object.assign({}, ...value)

    return { [item.id]: value }
}

function get_list_dir_data(item) {
    validate_data(item)

    const obj = {
        root_path: item.path,
        items: item.items
    }

    return { [item.id]: obj }
}

function get_double_input_list_data(item) {
    validate_data(item)

    return { [item.id]: item.items }
}

function get_file_data(item) {
    const file = document.getElementById(item.id)
    const value = file.textContent

    validate_data(item)

    return { [item.id]: value }
}

function validate_file_data(item) {
    const file = document.getElementById(item.id)

    if (!file.textContent) {
        throw `Field: ${item.id} -> Validation error`
    }
}

function set_file_data(item, value) {
    item.value = value
}

function get_toggler_between_data(item) {
    const checkbox = document.getElementById(item.id);
    const checkbox_value = checkbox.checked;
    const item_to_use = checkbox_value ? item.items[1] : item.items[0];

    const data_retrieval_function = data_retrieval_functions[item_to_use.type];
    const value = data_retrieval_function(item_to_use);

    validate_data(item_to_use)

    return { [item.id]: { [`is_${item.items[1].id}`]: checkbox_value, ...value } }
}

function set_toggler_between_data(item, value) {
    const bool = value[`is_${item.items[1].id}`]
    item.value = bool

    const item_to_use = bool ? item.items[1] : item.items[0];

    item_to_use.value = value[item_to_use.id]
}

function get_input_data(item) {
    const input = document.getElementById(item.id)
    let value = input.value

    validate_data(item)

    if (item.type === ITEM_TYPES.NUMBER) {
        value = Number(value)
    }

    return { [item.id]: value }
}

function validate_input_data(item) {
    const input = document.getElementById(item.id)

    if (!input.value) {
        throw `Field: ${item.id} -> Validation error`
    }
}

function set_input_data(item, value) {
    item.value = value
}

function get_select_data(item) {
    const select = document.getElementById(item.id)

    validate_data(item)
    if (item.require) {
        const value = select.options[select.selectedIndex].value

        if (item.options.find(x => x.index)) {
            return { [item.id]: item.options[select.selectedIndex].index }
        }
        return { [item.id]: value }
    }

    return { [item.id]: "" }
}

function validate_select_data(item) {
    const select = document.getElementById(item.id)


    if (select.selectedIndex < 0) {
        throw `Field: ${item.id} -> Validation error`
    }
}

function set_select_data(item, value) {
}

function run() {
    for (let block of blocks) {
        add_block(block)
    }
}

async function prepare_data() {
    blocks
        .find(x => x.id === "general")
        .items.find(x => x.id === "microphone")
        .options = await eel.get_microphones()()

    const sphinx_list_dirs = blocks
        .find(x => x.id === "sphinx")
        .items.find(x => x.id === "sphinx_list_dirs")

    sphinx_list_dirs.items = await eel.get_list_dir(sphinx_list_dirs.path)()
}

function add_block(block, index = -1) {
    const _block = gen_block(block.id);
    const title = gen_block_title(block.title);

    _block.append(title)

    if (index === 0) {
        root.prepend(_block)
    } else if (index === blocks.length - 1 || index === -1) {
        root.append(_block)
    } else {
        const div_after = root.children[index - 1];

        root.insertBefore(_block, div_after.nextSibling);
    }


    for (let item of block.items) {
        switch_type(item, _block)
    }

    const div = document.createElement("div")
    div.classList.add("button_section")

    const save_button = gen_button(block.id + "_save", "Save")
    const default_button = gen_button(block.id + "_save", "Default")

    default_button.addEventListener("click", async () => {
        const default_blocks = await eel.get_ui_default_settings()()
        const default_block = JSON.parse(default_blocks).filter(x => x.id === block.id)[0]
        const index = blocks.findIndex(x => x.id === block.id)

        blocks[index] = default_block
        if (block.id === "general") {
            await prepare_data()
        }

        const current_block = document.getElementById(block.id)
        current_block.remove()

        add_block(blocks[index], index)
        show_message("Settings were set to default", LOGGER_LEVEL.INFO)
    })


    save_button.addEventListener("click", async () => {
        let result = block.items.map(x => {
            const data_retrieval_function = data_retrieval_functions[x.type];
            if (data_retrieval_function) {
                const res = data_retrieval_function(x);

                const data_set_function = data_set_functions[x.type]

                if (data_set_function) {
                    data_set_function(x, res[x.id])
                }


                return res
            }
        })

        let data = Object.assign({}, ...result)


        await eel.save_part_settings(block.id, data)()
        show_message("Settings were successfully saved", LOGGER_LEVEL.INFO)
    })

    div.append(default_button)
    div.append(save_button)
    _block.append(div)
}

function switch_type(item, block) {
    const functionToCall = itemTypeToFunctionMap[item.type];
    if (functionToCall) {
        functionToCall(item, block);
    }
}


function add_select(item, block) {
    const { id, label, type, require, options, selected } = item

    const select_block = gen_input_block(id)
    const select_label = gen_input_label(label, id, require)
    const select = gen_select(id, options, selected)

    select_block.appendChild(select_label)
    select_block.appendChild(select)

    block.appendChild(select_block)
}

function gen_select(id, options, selected) {
    const select = document.createElement("select")
    select.classList.add("input")
    select.id = id

    options.forEach(x => {
        const option = document.createElement("option")
        option.textContent = x.name

        if (x.value) {
            option.value = x.value
        } else {
            option.name = x.name
        }

        if (selected === x.value) {
            option.selected = true
        }

        select.append(option)
    })

    return select
}


function add_list_dirs(item, block) {
    const { id, items, label } = item
    const list_block = document.createElement("div")
    list_block.textContent = label

    const list = document.createElement("div")
    list.classList.add("double_list")
    list.id = id + LIST_PREFIX

    list_block.append(list)

    block.append(list_block)

    renew_list_dirs(item)
}

async function renew_list_dirs(item) {
    const { id, path } = item
    const list = document.getElementById(id + LIST_PREFIX)

    item.items = await eel.get_list_dir(path)()

    list.innerHTML = ""

    const button = gen_button(id + "button", "Add")
    button.addEventListener("click", async () => {
        await eel.add_dir(path)()
        await renew_list_dirs(item)
    })

    list.append(button)

    const { items } = item

    items.forEach(x => {
        let block = document.createElement("div")
        block.classList.add("double_list_item")
        block.textContent = x

        block.addEventListener("contextmenu", async (event) => {
            event.preventDefault();
            const result = confirm(`Are you sure to delete ${x}?`)

            if (result) {
                await eel.remove_dir(path, x)()
                renew_list_dirs(item)
            }
        });

        list.append(block)
    })
}


function add_double_input_list(item, block) {
    const { id, items, first_label, second_label } = item
    const double_input_block = gen_double_input_list_block(id)

    const first_label_block = document.createElement("div")
    first_label_block.classList.add("double_list_label")
    first_label_block.textContent = first_label

    const first_list_block = document.createElement("div")
    first_list_block.classList.add("double_list")
    first_list_block.id = id + "1" + LIST_PREFIX

    first_label_block.append(first_list_block)

    const second_label_block = document.createElement("div")
    second_label_block.classList.add("double_list_label")
    second_label_block.textContent = second_label

    const second_list_block = document.createElement("div")
    second_list_block.classList.add("double_list")
    second_list_block.id = id + "2" + LIST_PREFIX

    second_label_block.append(second_list_block)

    double_input_block.append(first_label_block)
    double_input_block.append(second_label_block)

    block.append(double_input_block)

    renew_double_input_list(item, 0)
}


function renew_double_input_list(item, index) {
    const { id, items, first_label, second_label } = item

    const list1 = document.getElementById(id + "1" + LIST_PREFIX)
    const list2 = document.getElementById(id + "2" + LIST_PREFIX)

    list1.innerHTML = ""
    list2.innerHTML = ""

    let keys = Object.keys(items)

    list1.querySelectorAll(".double_list_item").forEach(x => {
        x.classList.remove("double_list_item")
    })

    if (keys.length === 0) {
        return
    }

    const first_button = gen_button(id + "button_1", "Add")
    first_button.addEventListener("click", () => {
        let result = prompt(`Add new ${first_label.toLowerCase()}`)

        if (result) {
            items[result] = {}
            renew_double_input_list(item, index)
        }
    })

    list1.append(first_button)

    keys.forEach((x, i) => {
        let block = document.createElement("div")
        block.classList.add("double_list_item")
        block.textContent = x
        if (i === index) {
            block.classList.add("list_selected")
        }

        block.addEventListener("click", () => {
            renew_double_input_list(item, i)
        })

        block.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            const result = confirm(`Are you sure to delete ${x}?`)

            if (result) {
                if (i === index && i === keys.length - 1) {
                    index--
                }

                delete items[x]

                renew_double_input_list(item, index)
            }
        });

        list1.append(block)
    })

    const second_button = gen_button(id + "button_2", "Add")
    second_button.addEventListener("click", () => {
        let result = prompt(`Add new ${second_label.toLowerCase()}`)

        if (result) {
            items[keys[index]].push(result)
            renew_double_input_list(item, index)
        }
    })

    list2.append(second_button)

    if (!items[keys[index]] || items[keys[index]].length === 0) {
        return
    }

    items[keys[index]].forEach(x => {
        let block = document.createElement("div")
        block.classList.add("double_list_item")
        block.textContent = x

        block.addEventListener("contextmenu", (event) => {
            event.preventDefault();
            const result = confirm(`Are you sure to delete ${x}?`)

            if (result) {
                items[keys[index]] = items[keys[index]].filter(y => y !== x)
                renew_double_input_list(item, index)
            }
        });

        list2.append(block)
    })
}

// SHIT CODE BUT WORKS !!!
function add_double_cb_list(item, block) {
    const { id, items, first_label, second_label } = item
    const double_cb_block = gen_double_cb_list_block(id)
    const double_cb_list_label1 = gen_double_cb_list_label(id + "1", first_label, items.map(x => {
        return { value: x.value, selected: x.selected }
    }), true)
    const double_cb_list_label2 = gen_double_cb_list_label(id + "2", second_label, items[0].items)

    double_cb_block.append(double_cb_list_label1)
    double_cb_block.append(double_cb_list_label2)

    block.append(double_cb_block)


    const items1 = document.getElementById(id + "1" + LIST_PREFIX).querySelectorAll(".double_cb_list_item")
    const items2 = document.getElementById(id + "2" + LIST_PREFIX).querySelectorAll(".double_cb_list_item")

    items1.forEach((x, index) => {
        if (index === 0) {
            x.classList.add("list_selected")
        }

        x.addEventListener("click", () => {
            items1.forEach(y => y.classList.remove("list_selected"))
            x.classList.add("list_selected")


            const lastDiv = double_cb_block.lastElementChild;

            if (lastDiv && lastDiv.tagName === "DIV") {
                double_cb_block.removeChild(lastDiv);
            }

            double_cb_block.append(gen_double_cb_list_label(id + "2", second_label, items[index].items))

            const items2 = document.getElementById(id + "2" + LIST_PREFIX).querySelectorAll(".double_cb_list_item")

            items2.forEach((x, index) => {
                x.querySelectorAll("input").forEach(y => {
                    y.addEventListener("change", (event) => {
                        const prev_items = document.getElementById(id + "1" + LIST_PREFIX).querySelectorAll(".double_cb_list_item")
                        const current_index = Array.from(prev_items).findIndex(item => item.classList.contains("list_selected"));

                        items[current_index].items[index].selected = event.currentTarget.checked
                    })
                })
            })
        })

        x.querySelectorAll("input").forEach(y => {
            y.addEventListener("change", (event) => {
                items[index].selected = event.currentTarget.checked
            })
        })


    })

    items2.forEach((x, index) => {
        x.querySelectorAll("input").forEach(y => {
            y.addEventListener("change", (event) => {
                const prev_items = document.getElementById(id + "1" + LIST_PREFIX).querySelectorAll(".double_cb_list_item")
                const current_index = Array.from(prev_items).findIndex(item => item.classList.contains("list_selected"));
                items[current_index].items[index].selected = event.currentTarget.checked
            })
        })
    })
}

function validate_double_cb_list_data(item) {
    let count = 0;
    item.items.forEach(x => {
        if (x.selected) {
            count++
            if (x.items.filter(y => y.selected).length === 0) {
                throw `Field: ${item.id} -> Validation error`
            }
        }
    })

    if (count === 0) {
        throw `Field: ${item.id} -> Validation error`
    }
}

function validate_list_dir_data(item) {
    if (item.items.length === 0) {
        throw `Field: ${item.id} -> Validation error`
    }
}

function validate_double_input_list_data(item) {
    if (Object.keys(item.items).length === 0) {
        throw `Field: ${item.id} -> Validation error`
    }


    Object.keys(item.items).forEach(x => {
        if (item.items[x].length === 0) {
            throw `Field: ${item.id} -> Validation error`
        }
    })
}

function gen_double_cb_list_label(id, label, items) {
    const block = document.createElement("div")
    block.classList.add("double_list_label")
    block.textContent = label

    const double_cb_list = gen_double_cb_list(id);

    items.forEach((x) => {
        double_cb_list.append(gen_double_cb_item(x.value, x.selected))
    })

    block.append(double_cb_list)

    return block
}

function gen_double_cb_item(value, selected) {
    const block = document.createElement("div")
    block.classList.add("double_cb_list_item")

    const checkbox = document.createElement("input")
    checkbox.setAttribute("type", "checkbox")
    checkbox.checked = selected

    const text = document.createElement("div")
    text.textContent = value

    block.append(checkbox)
    block.append(text)
    return block
}

function gen_double_cb_list(id) {
    const block = document.createElement("div")
    block.classList.add("double_list")
    block.id = id + LIST_PREFIX

    return block
}

function gen_double_cb_list_block(id) {
    const block = document.createElement("div")
    block.id = id + BLOCK_PREFIX
    block.classList.add("double_list_block")
    return block
}

function gen_double_input_list_block(id) {
    const block = document.createElement("div")
    block.id = id + BLOCK_PREFIX
    block.classList.add("double_list_block")
    return block
}

function add_toggler_between(item, block) {
    const { id, label, value, items } = item

    const on_change = (event) => {
        const item1 = document.getElementById(items[0].id + BLOCK_PREFIX)
        const item2 = document.getElementById(items[1].id + BLOCK_PREFIX)

        if (event.currentTarget.checked) {
            item2.classList.remove('hidden');
            item1.classList.add('hidden');
        } else {
            item2.classList.add('hidden');
            item1.classList.remove('hidden');
        }
    }

    const toggler = gen_toggler(id, label, value, on_change)

    block.append(toggler)

    switch_type(items[0], block)
    switch_type(items[1], block)

    const item1 = document.getElementById(items[0].id + BLOCK_PREFIX)
    const item2 = document.getElementById(items[1].id + BLOCK_PREFIX)

    if (value) {
        item2.classList.remove('hidden');
        item1.classList.add('hidden');
    } else {
        item2.classList.add('hidden');
        item1.classList.remove('hidden');
    }
}

function add_file_input(item, block) {
    const { id, label, value } = item

    const file_block = gen_file_block(id)
    const block_label = gen_file_label(label)
    const file_input = gen_file_input(id, label, value)

    file_block.append(block_label)
    file_block.append(file_input)
    block.append(file_block)
}

function gen_file_block(id) {
    const block = document.createElement("div")
    block.classList.add("block_file_label")
    block.id = id + BLOCK_PREFIX
    return block
}

function gen_file_label(label) {
    const div = document.createElement("div")
    div.textContent = label
    div.classList.add("block_file_label")
    return div
}

function gen_file_input(id, label, value) {
    const file_block = gen_file_input_block()
    const button = gen_button(id + "btn", "Select path")

    button.addEventListener("click", async () => {
        const text = document.getElementById(id)
        const res = await eel.get_file([])()
        text.textContent = res
    })

    const text = gen_file_input_text(id, value)

    file_block.append(button)
    file_block.append(text)
    return file_block
}

function gen_file_input_text(id, value) {
    const text = document.createElement("div")
    text.id = id
    text.textContent = value
    return text
}

function gen_file_input_block() {
    const block = document.createElement("div")
    block.classList.add("file_input")
    return block
}

function gen_block(id) {
    const block = document.createElement("div")
    block.classList.add("block")
    block.id = id
    return block
}

function gen_block_title(title) {
    const _title = document.createElement("h2")
    _title.classList.add("block_title")
    _title.textContent = title
    return _title
}

function add_input(item, block) {
    const { id, label, type, require, value } = item

    const input_block = gen_input_block(id)
    const input_label = gen_input_label(label, id, require)
    const input = gen_input(id, type, value, require)

    input_block.appendChild(input_label)
    input_block.appendChild(input)

    block.appendChild(input_block)
}

function gen_input_block(id) {
    const block = document.createElement("div")
    block.classList.add("block_input")
    block.id = id + BLOCK_PREFIX
    return block
}

function gen_input_label(text, id, require) {
    const label = document.createElement("label")
    label.classList.add("block_input_label")
    label.textContent = require ? text + "*" : text
    label.setAttribute("for", id)
    return label
}

function gen_input(id, type, value, require) {
    const input = document.createElement("input")
    input.classList.add("input")
    input.id = id
    input.setAttribute("type", type)
    input.setAttribute("value", value ? value : "")
    input.required = require
    return input
}

function add_button(item, block) {
    const { id, text, on_click } = item
    const button = gen_button(id, text, on_click)
    block.append(button)
}

function gen_button(id, text, on_click) {
    const button = document.createElement("div")
    button.classList.add("button")
    button.id = id
    button.textContent = text
    button.addEventListener("click", BUTTON_ON_CLICK_EVENTS[on_click])
    return button
}

function add_toggler(item, block) {
    const { id, label, value } = item
    const toggler = gen_toggler(id, label, value)
    block.append(toggler)
}

function gen_toggler(id, label, value, on_change = () => {
}) {
    const toggler_block = gen_toggler_block(id, label)
    const toggler_label = gen_toggler_label()
    const toggler_checkbox = gen_toggler_checkbox(id, value, on_change)
    const toggler_span = gen_toggler_span()

    toggler_label.appendChild(toggler_checkbox);
    toggler_label.appendChild(toggler_span);
    toggler_block.appendChild(toggler_label);
    return toggler_block;
}

function gen_toggler_block(id, label) {
    const toggler_block = document.createElement("div")
    toggler_block.classList.add("switch_block")
    toggler_block.textContent = label
    toggler_block.id = id + BLOCK_PREFIX
    return toggler_block
}

function gen_toggler_label() {
    const toggler_label = document.createElement("label")
    toggler_label.classList.add("switch")
    return toggler_label
}

function gen_toggler_checkbox(id, value, on_change) {
    const checkbox = document.createElement("input")
    checkbox.id = id
    checkbox.checked = value
    checkbox.setAttribute("type", "checkbox")
    checkbox.addEventListener("change", on_change)
    return checkbox
}

function gen_toggler_span() {
    const toggler_span = document.createElement("span")
    toggler_span.classList.add("slider")
    toggler_span.classList.add("round")
    return toggler_span
}

function double_create_multiply_list(input) {
    const { list, first_label, second_label } = input

    const multiply_div = create_el("div", "block_double_multiply_list")

    let items = list.map((item, index) => {
        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = item.label;
        checkbox.value = item.label;
        checkbox.checked = item.selected;

        let div = document.createElement("div")
        div.append(checkbox)
        div.classList.add("list_item")

        let label = document.createElement("label");
        label.appendChild(document.createTextNode(item.label));
        div.id = `${index}_${item.label}`
        div.append(label)

        label.addEventListener("click", function () {
            list.forEach((x, i) => {
                if (x.current) {
                    x.current = false
                    const prev_div = document.getElementById(`${i}_${x.label}`)
                    prev_div.classList = ["list_item"]
                }
            })

            list[index].current = true
            const current_div = document.getElementById(`${index}_${item.label}`)
            current_div.classList.add("list_item_active")
            updateMultiplySecondList(list[1].id, item, list, index, second_label);
        });

        checkbox.addEventListener("change", (event) => {
            const checked = event.currentTarget.checked;

            list[index].selected = checked
        })

        return div
    })

    let div = document.createElement("div")
    let title_div = create_el("div", "block_list_label", first_label)
    div.append(title_div)
    div.append(...items)
    multiply_div.append(div)

    div = document.createElement("div")
    div.id = list[1].id
    multiply_div.append(div)

    return multiply_div
}

function updateMultiplySecondList(id, selectedItem, list, index, label) {
    let secondListContainer = document.getElementById(id);
    secondListContainer.innerHTML = "";

    let title_div = create_el("div", "block_list_label", label)
    secondListContainer.append(title_div)

    selectedItem.items.forEach((item, i) => {
        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = item.label;
        checkbox.value = item.label;
        checkbox.checked = item.selected;

        let div = document.createElement("div")
        div.classList.add("list_item")
        div.append(checkbox)

        let label = document.createElement("label");
        label.appendChild(document.createTextNode(item.label));

        div.append(label)

        checkbox.addEventListener("change", (event) => {
            list[index].items[i].selected = event.currentTarget.checked
        })

        secondListContainer.appendChild(div);
    });
}
