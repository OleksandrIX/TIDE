import WaveSurfer from '../../vendor/wavesurfer/wavesurfer.esm.js'
import RecordPlugin from '../../vendor/wavesurfer/record.esm.js'

const voice_activity = document.querySelector("#voice_activity")
const voice_activity_session = document.querySelector("#session-name")
document.addEventListener("DOMContentLoaded", async () => {
    if (localStorage.getItem("session_id")) {
        await load_activity()
    }
});


let wavesurfer, record
let scrollingWaveform = true

const start_btn = document.querySelector(".session-control .start");
const stop_btn = document.querySelector(".session-control .pause");

async function load_activity() {
    const index_micro = JSON.parse(await eel.get_settings()())
    start_record(index_micro.general.microphone)
    voice_activity.style.cssText = `
               display:block;
        `;
    const session_id = localStorage.getItem("session_id")
    const response = await eel.get_session_name_by_id(session_id)()
    if (response.status !== 200)
        show_message(response.body.message, LOGGER_LEVEL.ERROR)
    if (voice_activity_session)
        voice_activity_session.innerHTML = `
        <a href="session.html?session_id=${session_id}" style="font-weight: bold; color: black">${response.body.name}</a>
    `
}

start_btn?.addEventListener('click', async () => {
    await load_activity()
})
stop_btn?.addEventListener('click', () => {
    record.stopRecording()
    voice_activity.innerHTML = ''
    voice_activity.style = '';
    if (voice_activity_session)
        voice_activity_session.style.dispay = "block"
    wavesurfer.destroy()
})


export function start_record(index_micro) {
    wavesurfer = WaveSurfer.create({
        container: '#voice_activity',
        waveColor: '#1E90FF',
        progressColor: '#32CD32',
        barGap: 1,
        barWidth: 1,
    })

    record = wavesurfer.registerPlugin(RecordPlugin.create({scrollingWaveform, renderRecordedAudio: false}))

    if (record.isRecording() || record.isPaused()) {
        record.stopRecording()
        return
    }
    record.startRecording(index_micro)
}

