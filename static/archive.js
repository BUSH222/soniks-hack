document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    fetchLogs();
    fetchChartData();
    setInterval(fetchLogs, 20000);
    setInterval(fetchChartData, 60000);
});

// panel 2
function fetchLogs() {
fetch('https://sonik.space/api/observations/')
    .then(res => res.json())
    .then(data => updateObsLog(data))
    .catch(err => console.error('Log fetch error:', err));
}

let lastTimestamp = null;
function updateObsLog(observations) {
    const log = document.getElementById('observationLog');
    observations.forEach(obs => {
        if (!lastTimestamp || new Date(obs.timestamp) > new Date(lastTimestamp)) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = `[${new Date(obs.timestamp).toLocaleTimeString()}] ID:${obs.id} ${obs.status}`;
        log.prepend(li);
        lastTimestamp = obs.timestamp;
        }
    });
while (log.children.length > 50) log.removeChild(log.lastChild);
}

// panel 3
let chart1, chart2, chart3;
function fetchChartData() {
fetch('https://sonik.space/api/observations/')
    .then(res => res.json())
    .then(data => {
    const labels = data.map(o => new Date(o.timestamp).toLocaleTimeString()).slice(-20);
    const snr = data.map(o => o.snr).slice(-20);
    const rssi = data.map(o => o.rssi).slice(-20);

    updateChart(chart1, labels, snr, 'SNR (dB)');
    updateChart(chart2, labels, rssi, 'RSSI (dBm)');
    updateChart(chart3, labels, data.map(o => o.success ? 1 : 0).slice(-20), 'Успех (1)/Неудача (0)');
    })
    .catch(err => console.error('Chart fetch error:', err));
}

function initCharts() {
    const ctx1 = document.getElementById('snrChart').getContext('2d');
    const ctx2 = document.getElementById('rssiChart').getContext('2d');
    const ctx3 = document.getElementById('successChart').getContext('2d');
    chart1 = new Chart(ctx1, makeConfig([], [], 'SNR (dB)'));
    chart2 = new Chart(ctx2, makeConfig([], [], 'RSSI (dBm)'));
    chart3 = new Chart(ctx3, makeConfig([], [], 'Статус'));  
}    

function makeConfig(labels, data, label) {
return {
    type: 'line',
    data: { labels, datasets: [{ label, data, fill: false, tension: 0.1 }] },
    options: {
    scales: {
        y: { title: { display: true, text: label } },
        x: { title: { display: true, text: 'Время' } }
    }
    }
};
}

function updateChart(chart, labels, data, label) {
chart.data.labels = labels;
chart.data.datasets[0].data = data;
chart.update();
}

initCharts();