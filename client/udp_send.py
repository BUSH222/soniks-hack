import osmosdr
import asyncio
from gnuradio import gr
from aiortc import RTCPeerConnection

class SDRToWebRTC(gr.top_block):
    def __init__(self, center_freq, samp_rate, bandwidth, rtc_channel):
        gr.top_block.__init__(self)

        # SDR source block
        self.sdr_source = osmosdr.source(args="numchan=1")
        self.sdr_source.set_sample_rate(samp_rate)
        self.sdr_source.set_center_freq(center_freq)
        self.sdr_source.set_bandwidth(bandwidth)
        self.sdr_source.set_gain(30)

        self.rtc_channel = rtc_channel
        self.sink = gr.sync_block(
            name="WebRTC Sink",
            in_sig=[gr.sizeof_gr_complex],
            out_sig=None,
        )
        self.sink.work = self.send_to_webrtc

        self.connect(self.sdr_source, self.sink)

    def send_to_webrtc(self, input_items, output_items):
        iq_samples = input_items[0]
        if self.rtc_channel.readyState == "open":
            self.rtc_channel.send(iq_samples.tobytes())
        return len(iq_samples)


async def run_webrtc_server(center_freq, samp_rate, bandwidth):
    pc = RTCPeerConnection()
    rtc_channel = pc.createDataChannel("sdr")
    tb = SDRToWebRTC(center_freq, samp_rate, bandwidth, rtc_channel)
    
    @pc.on("datachannel")
    async def on_datachannel(channel):
        print(f"Data channel {channel.label} is open")

    tb.start()
    await pc.close()
    tb.stop()
    tb.wait()


if __name__ == "__main__":
    CENTER_FREQ = 100.1e6
    BANDWIDTH = 1.024e6
    SAMPLE_RATE = 2.048e6

    asyncio.run(run_webrtc_server(CENTER_FREQ, SAMPLE_RATE, BANDWIDTH))
