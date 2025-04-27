import asyncio
import numpy as np
import time
import threading
from flask import Flask, request, render_template
from flask_sock import Sock
from gnuradio import gr
import osmosdr
from pipelines import pipelines
# from scipy.fft import fft, fftshift

app = Flask(__name__)
sock = Sock(app)

frequency = None
BANDWIDTH = 1.024e6//2
SAMPLE_RATE = 1.024e6

retransmitted_data = None
sdr_instance = None
sdr_thread = None
sdr_thread_stop_event = threading.Event()


class SDRToWebSocket(gr.top_block):
    def __init__(self, center_freq, samp_rate, bandwidth):
        super().__init__()
        self.sdr_source = osmosdr.source(args="numchan=1")
        self.sdr_source.set_sample_rate(samp_rate)
        self.sdr_source.set_center_freq(center_freq)
        self.sdr_source.set_bandwidth(bandwidth)
        self.sdr_source.set_gain(30)

        self.sink = WebSocketSink()
        self.connect(self.sdr_source, self.sink)

    def update_frequency(self, new_freq):
        """Update the SDR's center frequency."""
        self.sdr_source.set_center_freq(new_freq)
        print(f"SDR frequency updated to {new_freq} Hz")


class WebSocketSink(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="WebSocketSink",
            in_sig=[np.complex64],
            out_sig=None
        )

    def work(self, input_items, output_items):
        iq_data = input_items[0]
        fft_result = np.fft.fftshift(np.fft.fft(iq_data))
        magnitude = 20 * np.log10(np.abs(fft_result) + 1e-9)
        payload = magnitude.astype(np.float32).tobytes()
        asyncio.run(self.send_data(payload))
        return len(iq_data)

    async def send_data(self, data):
        global retransmitted_data
        retransmitted_data = data


@app.route('/start_conn', methods=['GET'])
def start_conn():
    global sdr_thread, sdr_thread_stop_event
    frequency_param = request.args.get('frequency')
    assert frequency_param is not None, "Frequency parameter is required"
    assert frequency_param.isdigit(), "Frequency must be a number"
    frequency = int(frequency_param)

    sdr_thread_stop_event.clear()
    sdr_thread = threading.Thread(target=start_sdr, args=(frequency,))
    sdr_thread.start()

    return render_template('reception.html', pipelines=pipelines)


@app.route('/stop_sdr', methods=['GET'])
def stop_sdr_endpoint():
    global sdr_thread, sdr_thread_stop_event
    if sdr_thread is not None:
        sdr_thread_stop_event.set()
        sdr_thread.join()
        sdr_thread = None
    return 'ok', 200


@app.route('/render_reception', methods=['GET'])
def reception():
    return render_template('reception.html', pipelines=pipelines)


@app.route('/change_freq', methods=['GET'])
def change_freq():
    global sdr_instance, sdr_thread, sdr_thread_stop_event

    frequency_param = request.args.get('frequency')
    assert frequency_param is not None, "Frequency parameter is required"
    assert frequency_param.isdigit(), "Frequency must be a number"
    frequency = int(frequency_param)

    if sdr_thread is not None and sdr_thread.is_alive() and sdr_instance is not None:
        # Update the SDR's center frequency using the instance
        sdr_instance.update_frequency(frequency)
        return f"Frequency changed to {frequency} Hz", 200
    else:
        return "SDR is not running", 400


@sock.route('/hi')
def send_data(ws):
    global retransmitted_data, sdr_thread, sdr_thread_stop_event
    try:
        while True:
            if retransmitted_data is not None:
                ws.send(retransmitted_data)
                retransmitted_data = None
                time.sleep(0.1)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if sdr_thread is not None:
            sdr_thread_stop_event.set()
            sdr_thread.join()
            sdr_thread = None
        print("WebSocket closed, SDR stopped")


def start_sdr(frequency):
    global sdr_thread_stop_event, sdr_instance
    sdr_instance = SDRToWebSocket(frequency, SAMPLE_RATE, BANDWIDTH)
    sdr_instance.start()
    print("Sending FFT data to an internal buffer (retransmitted_data)")
    try:
        while not sdr_thread_stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        sdr_instance.stop()
        sdr_instance.wait()
        sdr_instance = None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
