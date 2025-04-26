import socket
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftshift

# Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 1234
BUFFER_SIZE = 1472
SAMPLE_RATE = 2.048e6
FFT_SIZE = 1024*8

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

# Prepare for plotting
plt.ion()
fig, ax = plt.subplots()
freqs = np.linspace(-SAMPLE_RATE / 2, SAMPLE_RATE / 2, FFT_SIZE)
line, = ax.plot(freqs, np.zeros(FFT_SIZE))
ax.set_xlim(-SAMPLE_RATE / 2, SAMPLE_RATE / 2)
ax.set_ylim(-100, 40)  # Adjust based on signal strength
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Power (dB)")
ax.set_title("Real-Time Frequency Spectrum")
plt.show()
print('going')
try:
    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        iq_samples = np.frombuffer(data, dtype=np.complex64)

        if len(iq_samples) < FFT_SIZE:
            iq_samples = np.pad(iq_samples, (0, FFT_SIZE - len(iq_samples)), 'constant')
        fft_result = fftshift(fft(iq_samples[:FFT_SIZE]))

        power_spectrum = 20 * np.log10(np.abs(fft_result) + 1e-12) - 60  # whY -60 WHAT
        line.set_ydata(power_spectrum)
        plt.pause(0.01)

except Exception as e:
    print(print(e))
    sock.close()
    plt.close()
