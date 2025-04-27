// /static/archive.js

let statusChart, freqChart, successPie;

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  fetchLogs();
  fetchAllCharts();
  setInterval(fetchLogs, 20000);
  setInterval(fetchAllCharts, 60000);
});

// ——— Live log (panel 2) ———
function fetchLogs() {
  fetch('https://sonik.space/api/observations/')
    .then(r => r.json())
    .then(updateObsLog)
    .catch(e => console.error('Log fetch error:', e));
}

let lastTimestamp = null;
function updateObsLog(observations) {
  const log = document.getElementById('observationLog');
  observations.forEach(o => {
    if (!lastTimestamp || new Date(o.timestamp) > new Date(lastTimestamp)) {
      const li = document.createElement('li');
      li.textContent = `[${new Date(o.timestamp).toLocaleTimeString()}] ID:${o.id} ${o.status}`;
      log.prepend(li);
      lastTimestamp = o.timestamp;
    }
  });
  while (log.children.length > 50) log.removeChild(log.lastChild);
}

// ——— Charts init ———
function initCharts() {
  // Chart #1: Status counts (bar)
  const sCtx = document.getElementById('statusChart').getContext('2d');
  statusChart = new Chart(sCtx, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Количество', data: [], backgroundColor: '#2998e5' }] },
    options: { scales: { y: { beginAtZero: true, title: { display: true, text: 'Число наблюдений' } } } }
  });

  // Chart #2: Observations per minute (line)
  const fCtx = document.getElementById('freqChart').getContext('2d');
  freqChart = new Chart(fCtx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Наблюдений/мин', data: [], fill: false, tension: 0.3, borderColor: '#fe5e22' }] },
    options: {
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Число наблюдений' } },
        x: { title: { display: true, text: 'Время (HH:MM)' } }
      }
    }
  });

  // Chart #3: Success vs Failure (pie)
  const pCtx = document.getElementById('successPie').getContext('2d');
  successPie = new Chart(pCtx, {
    type: 'pie',
    data: {
      labels: ['Успех', 'Неудача'],
      datasets: [{ data: [0,0], backgroundColor: ['#2998e5','#fe5e22'] }]
    },
    options: { plugins: { legend: { position: 'bottom' } } }
  });
}

// ——— Fetch & update all charts ———
function fetchAllCharts() {
  fetch('https://sonik.space/api/observations/')
    .then(r => r.json())
    .then(data => {
      updateStatusChart(data);
      updateFreqChart(data);
      updateSuccessPie(data);
    })
    .catch(e => console.error('Chart fetch error:', e));
}

// ——— Chart 1: tally by status ———
function updateStatusChart(data) {
  const counts = {};
  data.forEach(o => counts[o.status] = (counts[o.status]||0) + 1);
  const labels = Object.keys(counts);
  statusChart.data.labels = labels;
  statusChart.data.datasets[0].data = labels.map(l => counts[l]);
  statusChart.update();
}

// ——— Chart 2: group by minute ———
function updateFreqChart(data) {
  const buckets = {};
  data.forEach(o => {
    const m = new Date(o.timestamp)
                .toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
    buckets[m] = (buckets[m]||0) + 1;
  });
  const labels = Object.keys(buckets).sort();
  freqChart.data.labels = labels;
  freqChart.data.datasets[0].data = labels.map(l => buckets[l]);
  freqChart.update();
}

// ——— Chart 3: success vs failure ———
function updateSuccessPie(data) {
  const ok = data.filter(o => o.success).length;
  const fail = data.length - ok;
  successPie.data.datasets[0].data = [ok, fail];
  successPie.update();
}
