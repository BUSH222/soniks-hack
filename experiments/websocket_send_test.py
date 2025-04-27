import numpy as np
import websockets
import asyncio
import osmosdr
import time
from gnuradio import gr, blocks


class SDRToWebSocket(gr.top_block):
    def __init__(self, center_freq, samp_rate, bandwidth, ws_uri):
        super().__init__()
        self.sdr_source = osmosdr.source(args="numchan=1")
        self.sdr_source.set_sample_rate(samp_rate)
        self.sdr_source.set_center_freq(center_freq)
        self.sdr_source.set_bandwidth(bandwidth)
        self.sdr_source.set_gain(30)

        # Convert complex to magnitude (float)
        self.complex_to_mag = blocks.complex_to_mag(1)

        self.to_char = blocks.float_to_char(1, 127)
        self.sink = WebSocketSink(ws_uri)

        # Chain: SDR -> complex_to_mag -> float_to_char -> WebSocket sink
        self.connect(self.sdr_source, self.complex_to_mag, self.to_char, self.sink)


class WebSocketSink(gr.sync_block):
    def __init__(self, ws_uri):
        gr.sync_block.__init__(
            self,
            name="WebSocketSink",
            in_sig=[np.int8],  # Use a NumPy type instead of gr.sizeof_char
            out_sig=None
        )
        self.ws_uri = ws_uri

    def work(self, input_items, output_items):
        data = input_items[0].tobytes()
        asyncio.run(self.send_data(data))
        return len(input_items[0])

    async def send_data(self, data):
        async with websockets.connect(self.ws_uri) as ws:
            await ws.send(data)


if __name__ == "__main__":
    CENTER_FREQ = 100.1e6
    BANDWIDTH = 1.024e6
    SAMPLE_RATE = 2.048e6
    WS_URI = "ws://localhost:8000/hi"

    tb = SDRToWebSocket(CENTER_FREQ, SAMPLE_RATE, BANDWIDTH, WS_URI)
    tb.start()
    print(f"Sending raw data over {WS_URI} ...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        tb.stop()
        tb.wait()
