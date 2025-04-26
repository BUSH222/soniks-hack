from flask import Flask, jsonify, request, render_template
from pipelines import pipelines
from flask_sock import Sock
import numpy as np
import websockets
import asyncio
import osmosdr
from gnuradio import gr, blocks
import time
import threading


app = Flask(__name__)
sock = Sock(app)

frequency = None
last_keep_alive = None
BANDWIDTH = 1.024e6
SAMPLE_RATE = 2.048e6

retransmitted_data = None

snr = 0
rssi = 0

# Thread management
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
        self.complex_to_mag = blocks.complex_to_mag(1)

        self.to_char = blocks.float_to_char(1, 127)
        self.sink = WebSocketSink()

        # Chain: SDR -> complex_to_mag -> float_to_char -> WebSocket sink
        self.connect(self.sdr_source, self.complex_to_mag, self.to_char, self.sink)


class WebSocketSink(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name="WebSocketSink",
            in_sig=[np.int8],
            out_sig=None
        )

    def work(self, input_items, output_items):
        data = input_items[0].tobytes()
        asyncio.run(self.send_data(data))
        return len(input_items[0])

    async def send_data(self, data):
        global retransmitted_data
        if retransmitted_data is None:
            retransmitted_data = data
        else:
            retransmitted_data += data



@app.route('/start_conn', methods=['GET'])
def start_conn():
    global sdr_thread, sdr_thread_stop_event
    frequency = request.args.get('frequency')
    assert frequency is not None, "Frequency parameter is required"
    assert frequency.isdigit(), "Frequency must be a number"
    frequency = int(frequency)

    # Reset the stop event and start the SDR thread
    sdr_thread_stop_event.clear()
    sdr_thread = threading.Thread(target=start_sdr, args=(frequency,))
    sdr_thread.start()

    return render_template('temp.html')


@app.route('/change_freq', methods=['GET'])
def change_freq():
    frequency = request.args.get('frequency')
    assert frequency is not None, "Frequency parameter is required"
    assert frequency.isdigit(), "Frequency must be a number"
    frequency = int(frequency)
    return 'ok', 200


@app.route('/stop_sdr', methods=['GET'])
def stop_sdr_endpoint():
    global sdr_thread, sdr_thread_stop_event
    if sdr_thread is not None:
        sdr_thread_stop_event.set()  # Signal the thread to stop
        sdr_thread.join()  # Wait for the thread to terminate
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
    print("Sending raw data to an internal variable")
    try:
        while not sdr_thread_stop_event.is_set():  # Check if the stop event is set
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        tb.stop()
        tb.wait()


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000)