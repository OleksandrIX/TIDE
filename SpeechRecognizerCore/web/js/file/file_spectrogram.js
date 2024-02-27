import WaveSurfer from '../../vendor/wavesurfer/wavesurfer.esm.js'
import Timeline from '../../vendor/wavesurfer/timeline.esm.js'
import RegionsPlugin from '../../vendor/wavesurfer/regions.esm.js'
import Zoom from '../../vendor/wavesurfer/zoom.esm.js'
import {
    show_file_info,
    show_diarization_in_table,
    show_diarization_speech_in_table
} from "./file_table.js";

document.addEventListener("DOMContentLoaded", async () => {
    const folder_name = get_param_from_url("folder_name", window.location.href)
    const file_path = get_param_from_url("file_path", window.location.href)
    await load_file_to_page(folder_name, file_path)
    await get_setting_denoise()
});


async function get_setting_denoise() {
    const response = await eel.get_settings_denoise()()
    if (response.is_model)
        document.querySelector('#rnn').checked = true
    if (response.is_spectral_gating)
        document.querySelector('#spectral_gating').checked = true
}

document.querySelector('#rnn').addEventListener('click', async () => await eel.set_settings_denoise("is_model", document.querySelector('#rnn').checked))
document.querySelector('#spectral_gating').addEventListener('click', async () => await eel.set_settings_denoise("is_spectral_gating", document.querySelector('#spectral_gating').checked))

export async function load_file_to_page(folder_name, file_path) {
    const file = await show_file_info(folder_name, file_path);
    show_file_in_spectrogram(file, folder_name, file_path)
    config_controls()

    await show_diarization_in_table(folder_name, file_path)
    await show_diarization_speech_in_table(folder_name, file_path)
}

const random = (min, max) => Math.random() * (max - min) + min
const randomColor = () => `rgba(${random(0, 255)}, ${random(0, 255)}, ${random(0, 255)}, 0.5)`

export async function load_diarization_to_page(folder_name, file_path) {
    const file_diarization = await eel.get_diarization_file_by_path(folder_name, file_path)()

    const diarization_data = file_diarization.body.file
    await show_diarization(diarization_data)
}

async function show_diarization(diarization_data) {
    wsRegions.clearRegions()
    if (diarization_data) {
        let speaker_colors = new Map()
        for (let i = 0; i < diarization_data.data.length; i++) {
            const diarization_element = diarization_data.data[i].split(' ');
            if (!speaker_colors.has(diarization_element[2]))
                speaker_colors.set(diarization_element[2], randomColor());

            wsRegions.addRegion({
                start: parseFloat(diarization_element[0]),
                end: parseFloat(diarization_element[1]),
                content: diarization_element[2],
                color: speaker_colors.get(diarization_element[2]),
                drag: false,
                resize: false,
            })
        }
    }
}

export const wavesurfer = Object(WaveSurfer).create({
    container: '#spectrogram',
    waveColor: "#1E90FF",
    progressColor: "#32CD32",
    height: 150,
    maxPxPerSec: 1000,
    cursorWidth: 1,
    cursorColor: "black",
    normalize: true,
    responsive: true,
    fillParent: true,
    backend: 'MediaElement',
    splitChannels: true,
    barGap: 1,
    barWidth: 1,
    plugins: [
        Timeline.create({
            container: '#spectrogram',
            primaryColor: "#000000",
            secondaryColor: "#000000",
            primaryFontColor: "#000000",
            secondaryFontColor: "#000000",
        }),
        Zoom.create()
    ]
});

// Documentation 🔥

wavesurfer.clearRegions = function () {
    this.regions && this.regions.clear()
}

const wsRegions = wavesurfer.registerPlugin(RegionsPlugin.create())


/**
 * Adds volume, zoom default settings
 */
function config_controls() {
    // Config Volume
    const volume_input = document.querySelector(`#volume-input`)
    const on_change_volume = function (e) {
        wavesurfer.setVolume(Number(e.target.value))
    };
    volume_input.addEventListener('input', on_change_volume)
    volume_input.addEventListener('change', on_change_volume)
}

function show_file_in_spectrogram(file, folder_name, file_path) {
    wavesurfer.load(file.data).then(async () => {
        await load_diarization_to_page(folder_name, file_path)
    })

}

let is_playing = false
const play_pause_img = document.querySelector(`.play-pause img`)

export function play_pause_audio() {
    wavesurfer.playPause()
    is_playing = !is_playing

    let img_src
    if (is_playing) {
        img_src = './assets/icons/pause_circle.svg'
        append_logs("Audio has paused", LOGGER_LEVEL.INFO)
    } else {
        img_src = './assets/icons/play_circle.svg'
        append_logs("Playing audio", LOGGER_LEVEL.INFO)

    }

    play_pause_img.setAttribute('src', img_src)
}

export function stop_audio() {
    wavesurfer.stop()
    is_playing = false
    const img_src = './assets/icons/play_circle.svg'
    play_pause_img.setAttribute('src', img_src)
    append_logs("Audio has stopped", LOGGER_LEVEL.INFO)
}


wavesurfer.on('finish', stop_audio)