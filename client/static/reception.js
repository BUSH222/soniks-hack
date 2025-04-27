const SAMPLE_RATE = 1.024e6;

const frequencyCanvas = document.getElementById('frequencyCanvas');
const frequencyCtx = frequencyCanvas.getContext('2d');

const waterfallCanvas = document.getElementById('waterfallCanvas');
const waterfallCtx = waterfallCanvas.getContext('2d');

const ws = new WebSocket("/hi");

ws.onopen = () => {
  console.log("WebSocket connected");
};

ws.onmessage = (event) => {
  // Parse incoming data as an ArrayBuffer of float32 samples
  event.data.arrayBuffer().then(buffer => {
    const floatData = new Float32Array(buffer);
    const n = floatData.length;

    const freqAxis = new Array(n);
    for (let i = 0; i < n; i++) {
      freqAxis[i] = ((i - n / 2) * SAMPLE_RATE) / n;
    }

    // Find min/max for frequency and dB range
    let freqMin = freqAxis[0];
    let freqMax = freqAxis[0];
    let dbMin = floatData[0];
    let dbMax = floatData[0];

    for (let i = 1; i < n; i++) {
      if (freqAxis[i] < freqMin) freqMin = freqAxis[i];
      if (freqAxis[i] > freqMax) freqMax = freqAxis[i];
      if (floatData[i] < dbMin) dbMin = floatData[i];
      if (floatData[i] > dbMax) dbMax = floatData[i];
    }
    frequencyCtx.clearRect(0, 0, frequencyCanvas.width, frequencyCanvas.height);

    frequencyCtx.fillStyle = '#0080ff';
    for (let i = 0; i < n; i++) {
      const x = (freqAxis[i] - freqMin) / (freqMax - freqMin) * frequencyCanvas.width;
      const y = frequencyCanvas.height - (floatData[i] - dbMin) / (dbMax - dbMin) * frequencyCanvas.height;
      frequencyCtx.fillRect(x, y, 1, frequencyCanvas.height - y);
    }

    const imageData = waterfallCtx.getImageData(0, 0, waterfallCanvas.width, waterfallCanvas.height - 1);
    waterfallCtx.putImageData(imageData, 0, 1);

    for (let i = 0; i < n; i++) {
      const x = (freqAxis[i] - freqMin) / (freqMax - freqMin) * waterfallCanvas.width;
      const intensity = (floatData[i] - dbMin) / (dbMax - dbMin);
      let color;
      if (intensity > 0.8) {
        color = `rgb(255, ${Math.floor(255 * (1 - intensity))}, 0)`; // Red to Orange
      } else if (intensity > 0.6) {
        color = `rgb(255, 255, ${Math.floor(255 * (1 - intensity))})`; // Orange to Yellow
      } else if (intensity > 0.4) {
        color = `rgb(${Math.floor(255 * intensity)}, 255, 255)`; // Yellow to White
      } else if (intensity > 0.2) {
        color = `rgb(0, ${Math.floor(255 * intensity)}, 255)`; // White to Light Blue
      } else {
        color = `rgb(0, 0, ${Math.floor(255 * intensity)})`; // Light Blue to Dark Blue
      }

      waterfallCtx.fillStyle = color;
      waterfallCtx.fillRect(x, 0, 1, 1); // Draw at the top of the canvas
    }
  });
};

ws.onclose = () => {
  console.log("WebSocket disconnected");
};