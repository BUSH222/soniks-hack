import osmosdr
import time
from gnuradio import gr, blocks


class SDRToUDP(gr.top_block):
    def __init__(self, center_freq, samp_rate, bandwidth, udp_host, udp_port):
        gr.top_block.__init__(self)

        # SDR source block
        self.sdr_source = osmosdr.source(args="numchan=1")
        self.sdr_source.set_sample_rate(samp_rate)
        self.sdr_source.set_center_freq(center_freq)
        self.sdr_source.set_bandwidth(bandwidth)
        self.sdr_source.set_gain(30)

        # UDP sink block
        self.udp_sink = blocks.udp_sink(
            itemsize=gr.sizeof_gr_complex,
            host=udp_host,
            port=udp_port,
            payload_size=1472,
        )

        self.connect(self.sdr_source, self.udp_sink)


if __name__ == "__main__":
    CENTER_FREQ = 100.1e6
    BANDWIDTH = 1.024e6
    SAMPLE_RATE = 2.048e6
    UDP_HOST = "127.0.0.1"
    UDP_PORT = 1234

    tb = SDRToUDP(CENTER_FREQ, SAMPLE_RATE, BANDWIDTH, UDP_HOST, UDP_PORT)
    tb.start()

    print(f"Streaming raw I/Q data from {CENTER_FREQ/1e6} MHz to {UDP_HOST}:{UDP_PORT}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        tb.stop()
        tb.wait()
