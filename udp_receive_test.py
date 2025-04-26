import socket
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftshift

# Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 1234
BUFFER_SIZE = 1472
SAMPLE_RATE = 2.048e6
FFT_SIZE = 1024
WATERFALL_HEIGHT = 200

GRAPHS_MINLIM = -80
GRAPHS_MAXLIM = -20

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

plt.ion()
fig, (ax_spectrum, ax_waterfall) = plt.subplots(2, 1, figsize=(10, 8))

freqs = np.linspace(-SAMPLE_RATE / 2, SAMPLE_RATE / 2, FFT_SIZE)
line, = ax_spectrum.plot(freqs, np.zeros(FFT_SIZE))
ax_spectrum.set_xlim(-SAMPLE_RATE / 2, SAMPLE_RATE / 2)
ax_spectrum.set_ylim(GRAPHS_MINLIM, GRAPHS_MAXLIM)
ax_spectrum.set_xlabel("Frequency (Hz)")
ax_spectrum.set_ylabel("Power (dB)")
ax_spectrum.set_title("Real-Time Frequency Spectrum")

# Waterfall spectrogram plot
waterfall_data = np.zeros((WATERFALL_HEIGHT, FFT_SIZE))
waterfall_img = ax_waterfall.imshow(
    waterfall_data,
    aspect="auto",
    extent=[-SAMPLE_RATE / 2, SAMPLE_RATE / 2, 0, WATERFALL_HEIGHT],
    origin="lower",
    cmap="viridis",
)
ax_waterfall.set_xlabel("Frequency (Hz)")
ax_waterfall.set_ylabel("Time (frames)")
ax_waterfall.set_title("Waterfall Spectrogram")

plt.tight_layout()
plt.show()

try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        iq_samples = np.frombuffer(data, dtype=np.complex64)
        if len(iq_samples) < FFT_SIZE:
            iq_samples = np.pad(iq_samples, (0, FFT_SIZE - len(iq_samples)), 'constant')
        fft_result = fftshift(fft(iq_samples[:FFT_SIZE]))
        power_spectrum = 20 * np.log10(np.abs(fft_result) + 1e-12) - 60  # WHAT
        line.set_ydata(power_spectrum)
        waterfall_data = np.roll(waterfall_data, -1, axis=0)
        waterfall_data[-1, :] = power_spectrum
        waterfall_img.set_data(waterfall_data)
        waterfall_img.set_clim(np.min(waterfall_data), np.max(waterfall_data))

        plt.pause(0.01)

except KeyboardInterrupt:
    print("Stopping...")
    sock.close()
    plt.close()
