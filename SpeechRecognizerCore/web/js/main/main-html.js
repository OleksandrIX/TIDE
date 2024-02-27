/**
 *
 * @param file_explorer - {
 *     folder_1: [file_1, file_2],
 *     folder_2: [file_1, file_2],
 * }
 * @param accordion_name - str
 * @returns {string}
 */
function get_file_explorer_card(file_explorer, accordion_name) {
    let temp = `
    <table>
        <tr>
            <th>
                <label class="file_upload_label" for="file-upload" onclick="select_file_upload()">Upload Audio</label>
                <p class="file_name"></p>
            </th>
            <th>
                <button onclick="init_file_upload()">
                    <img class="file_upload_img" src="../../assets/icons/upload_file.svg" alt="upload">
                </button>
            </th>
        </tr>
    </table>`

    for (const directory in file_explorer) {
        temp +=
        `
        <table>
            <tr>
                <div class="${accordion_name}">
                    <div class="ac">
                        <h2 class="ac-header">
                            <button type="button" class="ac-trigger">${directory}</button>
                        </h2>
                        <div class="ac-panel">
        `
        for (const file of file_explorer[directory]) {
            temp += `
                            <p class="ac-text">
                                <a href="file.html?file_path=${file}&folder_name=${directory}"> ${file}</a>
                                <button onclick="delete_file('${directory}', '${file}')"><img src="../../assets/icons/delete.svg" alt="delete"></button>
                            </p>
            `
        }
    }
    temp += `
                        </div>
                    </div>
                </div>
            </tr>
        </table>
        `

    return temp
}
