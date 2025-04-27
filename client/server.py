import asyncio
import numpy as np
import time
import threading
from flask import Flask, request, render_template
from flask_sock import Sock
from gnuradio import gr, blocks
import osmosdr
# from scipy.fft import fft, fftshift  # Or "numpy.fft" if you prefer

app = Flask(__name__)
sock = Sock(app)

frequency = None
BANDWIDTH = 1.024e6//2
SAMPLE_RATE = 1.024e6

retransmitted_data = None
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

        # We now remove complex_to_mag and float_to_char to preserve the raw complex data
        # and feed it directly to our sink:
        self.sink = WebSocketSink()

        # Use np.complex64 as the input signature
        # (Many SDR sources produce complex64 samples by default)
        # The direct connection will output raw I/Q to WebSocketSink
        self.connect(self.sdr_source, self.sink)


class WebSocketSink(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="WebSocketSink",
            in_sig=[np.complex64],  # Accept raw I/Q complex data
            out_sig=None
        )

    def work(self, input_items, output_items):
        # input_items[0] is a numpy array of complex64
        iq_data = input_items[0]
        # For demonstration, compute an FFT for the entire block
        # (In practice, chunk appropriately or buffer across calls)
        # Example using numpy.fft:
        fft_result = np.fft.fftshift(np.fft.fft(iq_data))
        magnitude = 20 * np.log10(np.abs(fft_result) + 1e-9)

        # Convert to float32 bytes or pick another format (e.g. JSON)
        # The client can parse Float32Array on the frontend
        payload = magnitude.astype(np.float32).tobytes()

        # Store the payload for the WebSocket route to send
        asyncio.run(self.send_data(payload))
        return len(iq_data)

    async def send_data(self, data):
        global retransmitted_data
        # Overwrite or append depending on your preference
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

    return render_template('temp.html')


@app.route('/stop_sdr', methods=['GET'])
def stop_sdr_endpoint():
    global sdr_thread, sdr_thread_stop_event
    if sdr_thread is not None:
        sdr_thread_stop_event.set()
        sdr_thread.join()
        sdr_thread = None
    return 'ok', 200


@sock.route('/hi')
def send_data(ws):
    global retransmitted_data
    while True:
        if retransmitted_data is not None:
            ws.send(retransmitted_data)
            retransmitted_data = None
            time.sleep(0.1)


def start_sdr(frequency):
    global sdr_thread_stop_event
    tb = SDRToWebSocket(frequency, SAMPLE_RATE, BANDWIDTH)
    tb.start()
    print("Sending FFT data to an internal buffer (retransmitted_data)")
    try:
        while not sdr_thread_stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        tb.stop()
        tb.wait()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)