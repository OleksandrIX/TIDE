/**
 * file: {
 *     name: str,
 *     path: str,
 *     duration: number (seconds)
 *     size: number (MB)
 *     date: str
 *     data: str (base64)
 * }
 * @param file
 */
function get_file_info_card(file) {
    return `
<div class="table_container">
    <table class="file-card">
        <tr>
            <th>Name</th>
            <th id="file_name_th">${file.name}</th>
            <th>
                <button onclick="show_message('Does not work',LOGGER_LEVEL.WARN)"><img src="./assets/icons/edit.svg" alt="edit"></button>
            </th>
        </tr>
        <tr>
            <th>Duration</th>
            <th>${file.duration} s.</th>
            <th></th>
        </tr>
        <tr>
            <th>Size</th>
            <th>${file.size} KB</th>
            <th></th>
        </tr>
        <tr>
            <th>Creation Date</th>
            <th>${file.date}</th>
            <th></th>
        </tr>
        <tr>
            <th>Path</th>
            <th id="file_path_th">${file.path}</th>
            <th></th>
        </tr>
    </table>
</div>
    `
}

/**
 * predicted_language {
 *     language: en,
 *     language_probabilities: {
 *         en: 90,
 *         ua: 10,
 *         es: 0
 *     },
 *     language_tags: ['en-US', 'en-UK'],
 * }
 * folder_name: str
 * file_name: str
 *
 * @param predicted_language
 */
async function get_language_table_card(predicted_language) {
    if (!predicted_language) {
        return `<div>
                    <p><b>UNKNOWN</b></p>
                </div>`
    }

    let all_predictions = ""

    for (const prediction in predicted_language.language_probabilities) {
        all_predictions += `${prediction}: ${Math.round(predicted_language.language_probabilities[prediction])}%<br>`
    }

    let language_tags = Array.of(predicted_language.language_tags).join("<br>");

    const language_block =
        `<div>
                <p class="all-predication">
                    <span class="label">All Predictions</span>
                    <br>
                    <span class="value">${all_predictions}</span>
                </p>
        
                <p class="language">
                    <span class="label">Language</span>
                    <br>
                    <span class="value" id="language_tags_th">${language_tags}</span>
                </p>
            </div>`

    return language_block
}

/**
 * speech: str
 * @param speech
 */
function get_speech_table_card(speech) {
    if (!speech) {
        return `<table>
                    <tr>
                        <th style="width: 15%">Recognized text:</th>
                        <td id="speech_th">UNKNOWN</td>
                    </tr>
                 </table>`
    }
    return `<table>
                <tr>
                    <th style="width: 15%">Recognized text:</th>
                    <td id="speech_th">${speech}</td>
                </tr>
            </table>`
}

async function get_diarization_table_card(folder_name,
                                          diarization_data) {
    if (!diarization_data.file) {
        return `<table id="diarization-table">
                    <tr>
                        <th style="width: 15%">All diarizations data</th>
                        <th id="diarization-unknown">UNKNOWN</th>
                        <th></th>
                    </tr>
                </table>`
    }
    let tableHtml = '<table id="diarization-table">';
    tableHtml += `<tr>
                    <th style="text-align: center;">Duration</th>
                    <th style="text-align: center;">Speaker</th>
                    <th style="text-align: center;">Language</th>
                    <th style="text-align: center;">Recognized text</th>
                    <th style="text-align: center;">Sound</th>
                  </tr>`;

    for (let i = 0; i < diarization_data.file.data.length; i++) {
        const [startTime, endTime, tag] = diarization_data.file.data[i].split(' ');
        const audio_data = await get_audio_diarization_data(folder_name, `${diarization_data.file.path}_${startTime}_${endTime}_${tag}.wav`);
        tableHtml += `<tr id="${diarization_data.file.diarization_audio_files[i]}">
                        <td style="text-align: center; width: 10%">${startTime} s. - ${endTime} s.</td>
                        <td style="text-align: center; width: 10%">${tag}</td>
                        <td class="diarization_language" style="text-align: center; width: 10%"></td>
                        <td class="diarization-speech-cell" style="text-align: center; width: 50%"></td>
                        <td style="width: 20%"><audio style="width: 100%;" src='${audio_data.file.data}' controls>
                        </audio></td>
                       </tr>`;
    }

    tableHtml += '</table>';

    return tableHtml;
}