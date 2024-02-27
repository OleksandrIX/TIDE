const recorder_data_canvas = document.getElementById('recorded-data')
const trigger_words_canvas = document.getElementById('trigger-words')
const total_words_canvas = document.getElementById('total-words')
const multi_data_canvas = document.getElementById('multi-data')

const plugin = {
    id: 'customCanvasBackgroundColor',
    beforeDraw: (chart, args, options) => {
        const { ctx } = chart;
        ctx.save();
        ctx.globalCompositeOperation = 'destination-over';
        ctx.fillStyle = options.color || '#99ffff';
        ctx.fillRect(0, 0, chart.width, chart.height);
        ctx.restore();
    }
};

const colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#bcbd22",
    "#7f7f7f",
    "#c02942",
    "#53777a",
    "#f7b807",
    "#c7c7c7",
    "#cccccc",
    "#ffff00",
    "#000000",
]

document.addEventListener('DOMContentLoaded', load_chart_js)

async function load_chart_js() {
    const response = await eel.get_statistic()()

    if (response.status !== 200) {
        return show_message(response.body.message, LOGGER_LEVEL.ERROR)
    }

    const statistic = response.body.statistic

    load_recorder_data_statistic(statistic)
    load_trigger_word_count(statistic)
    load_total_words_count(statistic)
    load_multi_data_statistic(statistic)
}

function load_multi_data_statistic(statistic) {
    const statistic_per_day = statistic.statistic_per_day
    let data = statistic_per_day.map(({ date, count, trigger_count, word_count }) => ({ date, count, trigger_count, word_count }));

    let x_values = data.map(row => row.date)
    let y1_values = data.map(row => row.count)
    let y2_values = data.map(row => row.trigger_count)
    let y3_values = data.map(row => row.word_count)

    let back_colors = shuffle(colors)

    new Chart(multi_data_canvas, {
        type: "bar",
        data: {
            labels: x_values,
            datasets: [{
                label: "Count",
                data: y1_values,
                fill: false
            }, {
                label: "Triggers",
                data: y2_values,
                fill: false
            }, {
                label: "Word count",
                data: y3_values,
                fill: false
            }]
        }
    })
}

function load_recorder_data_statistic(statistic) {
    const statistic_per_day = statistic.statistic_per_day
    let data = statistic_per_day.map(({ date, count }) => ({ date, count }));

    let x_values = data.map(row => row.date)
    let y_values = data.map(row => row.count)
    let back_colors = shuffle(colors)

    new Chart(recorder_data_canvas, {
        type: 'bar',
        data: {
            labels: x_values,
            datasets: [
                {
                    label: 'Recorder interceptions per day',
                    data: y_values,
                }
            ]
        },
        options: {
            plugins: {
                customCanvasBackgroundColor: {
                    color: 'white',
                }
            }
        },
        plugins: [plugin],
    })
}

function load_trigger_word_count(statistic) {
    const statistic_per_day = statistic.statistic_per_day
    let data = statistic_per_day.map(({ date, trigger_count }) => ({ date, trigger_count }));

    let x_values = data.map(row => row.date)
    let y_values = data.map(row => row.trigger_count)
    let back_colors = shuffle(colors)

    new Chart(trigger_words_canvas, {
        type: 'line',
        data: {
            labels: x_values,
            datasets: [
                {
                    label: 'Recorder alerts per day',
                    data: y_values,
                    backgroundColor: back_colors,
                }
            ]
        },
        options: {
            plugins: {
                customCanvasBackgroundColor: {
                    color: 'white',
                }
            }
        },
        plugins: [plugin],
    })
}

function load_total_words_count(statistic) {
    const statistic_per_day = statistic.statistic_per_day
    let data = statistic_per_day.map(({ date, word_count }) => ({ date, word_count }));

    new Chart(total_words_canvas, {
        type: 'line',
        data: {
            labels: data.map(row => row.date),
            datasets: [
                {
                    label: 'Total words count per day',
                    data: data.map(row => row.word_count)
                }
            ]
        },
        options: {
            plugins: {
                customCanvasBackgroundColor: {
                    color: 'white',
                }
            }
        },
        plugins: [plugin],
    })
}

function random_hex_color() {
    let n = (Math.random() * 0xfffff * 1000000).toString(16);
    return '#' + n.slice(0, 6);
}

function shuffle(array) {
    return array.sort(() => Math.random() - 0.5);
}
