import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, decimate, cheby1, sosfilt, spectrogram
from config import CONFIG
from scipy.constants import c

def lowpass_filter_decimate(data, cutoff_freq, original_sampling_rate, decimation_factor, filter_order=8):
    """
    Applies a low-pass filter to the data and then decimates it.

    Args:
        data (array-like): The input data.
        cutoff_freq (float): The cutoff frequency of the low-pass filter (in Hz).
        original_sampling_rate (float): The original sampling rate of the data (in Hz).
        decimation_factor (int): The decimation factor.
        filter_order (int, optional): The order of the Butterworth filter. Defaults to 8.

    Returns:
        numpy.ndarray: The filtered and decimated data.
    """
    # Normalize the cutoff frequency to Nyquist frequency
    nyquist_freq = 0.5 * original_sampling_rate
    normalized_cutoff = cutoff_freq / nyquist_freq

    # Design the Butterworth filter
    b, a = butter(filter_order, normalized_cutoff, btype='low', analog=False)

    # Apply the filter using filtfilt for zero-phase filtering
    filtered_data = filtfilt(b, a, data)

    # Decimate the filtered data
    decimated_data = decimate(filtered_data, decimation_factor, ftype='fir')
    
    #decimated_data = decimate(data, decimation_factor, ftype='fir')

    return decimated_data

def highpass_filter(data, cutoff_freq, sampling_rate, filter_order=8):
    """
    Applies a high-pass filter to the data.

    Args:
        data (array-like): The input data.
        cutoff_freq (float): The cutoff frequency of the high-pass filter (in Hz).
        sampling_rate (float): The sampling rate of the data (in Hz).
        filter_order (int, optional): The order of the Butterworth filter. Defaults to 8.

    Returns:
        numpy.ndarray: The filtered data.
    """
    # Normalize the cutoff frequency to Nyquist frequency
    nyquist_freq = 0.5 * sampling_rate
    normalized_cutoff = cutoff_freq / nyquist_freq

    # Design the Butterworth filter
    b, a = butter(filter_order, normalized_cutoff, btype='high', analog=False)

    # Apply the filter using filtfilt for zero-phase filtering
    filtered_data = filtfilt(b, a, data)

    return filtered_data

def highpass_chebyshev(data, cutoff_freq, sampling_rate, filter_order=6, ripple_db=0.5):
    """
    Applies a Chebyshev Type I high-pass filter using second-order sections (SOS).
    
    Args:
        data (array-like): Input signal.
        cutoff_freq (float): Cutoff frequency in Hz.
        sampling_rate (float): Sampling rate in Hz.
        filter_order (int): Filter order (default is 6).
        ripple_db (float): Maximum passband ripple in dB (default is 0.5 dB).

    Returns:
        numpy.ndarray: Filtered signal.
    """
    nyquist_freq = 0.5 * sampling_rate
    normalized_cutoff = cutoff_freq / nyquist_freq

    # Design the Chebyshev Type I high-pass filter
    sos = cheby1(filter_order, ripple_db, normalized_cutoff, btype='high', analog=False, output='sos')

    # Apply the filter with zero-phase distortion
    filtered_data = sosfilt(sos, data)

    return filtered_data


def compute_spectrogram_and_max_freq(signal, sampling_rate, nfft=1024, noverlap=512, power_threshold=-50):
    """
    Computes the spectrogram and extracts the dominant frequency at each time step, 
    setting it to zero if below a power threshold.

    Args:
        signal (array-like): The input signal.
        sampling_rate (float): The sampling rate in Hz.
        nfft (int, optional): Number of FFT points. Defaults to 1024.
        noverlap (int, optional): Number of overlapping samples. Defaults to 512.
        power_threshold (float, optional): Power threshold in dB. Defaults to -50 dB.

    Returns:
        freqs (ndarray): Frequency bins.
        times (ndarray): Time bins.
        Sxx (ndarray): Spectrogram power.
        max_freqs (ndarray): Dominant frequency at each time step (zero if below threshold).
    """
    # Compute spectrogram
    freqs, times, Sxx = spectrogram(signal, fs=sampling_rate, nperseg=nfft, noverlap=noverlap)

    # Convert power to dB
    Sxx_dB = 10 * np.log10(Sxx + 1e-10)  # Add small value to avoid log(0)

    # Find dominant frequency at each time step
    max_freq_indices = np.argmax(Sxx, axis=0)  # Find index of max power in each time step
    max_powers = Sxx_dB[max_freq_indices, np.arange(len(times))]  # Get corresponding power values

    # Apply threshold: If max power < threshold, set frequency to 0
    max_freqs = freqs[max_freq_indices] * (max_powers > power_threshold)

    # Plot the spectrogram
    # plt.figure(figsize=(10, 6))
    # plt.pcolormesh(times, freqs, Sxx_dB, shading='auto', cmap='plasma')
    # plt.colorbar(label='Power (dB)')
    # plt.xlabel("Time (s)")
    # plt.ylabel("Frequency (Hz)")
    # plt.title("Spectrogram")
    # plt.show()

    return freqs, times, Sxx, max_freqs

decimation = 100

# Sampling rate in Hz
sampling_rate = 6e6 / decimation  # 4 million samples per second

f_prime = np.fromfile(open(CONFIG.file_name), dtype=np.complex64)
#f_prime = np.fromfile(open("output.bin"), dtype=np.complex64)
#f = np.fromfile(open("output.bin"), dtype=np.complex64)

#f = np.fromfile(open("1MHz_TEST"), dtype=np.complex64)
#f = np.fromfile(open("feb19.bin"), dtype=np.complex64)
#f = np.fromfile(open("1MHz_TEST_VECTOR"), dtype=np.complex64)
#f_prime = np.fromfile(open("mar4.bin"), dtype=np.complex64)
f_high = highpass_chebyshev(f_prime, 750, 6e6)
f = lowpass_filter_decimate(f_high, 1.5e6/decimation, 6e6, decimation, 6)

freqs, times, Sxx, max_freqs = compute_spectrogram_and_max_freq(f, sampling_rate, 256, 128, -99)

#plt.plot(max_freqs)


velocities = (max_freqs * c) / (2 * 85e9 + max_freqs)

plt.figure(figsize=(10, 6))
plt.plot(velocities)

print(f"max velocity: {max(velocities)}")


#print(1.5e6/decimation)

#print(len(f))

plt.figure(figsize=(10, 6))
plt.plot(f)
#plt.show()
plt.savefig(CONFIG.output_file_prefix + "_time_domain.png")

# Perform FFT
fft_result = np.fft.fft(f)
fft_magnitude = np.abs(fft_result)



# Calculate frequency bins
frequencies = np.fft.fftfreq(len(f), 1 / sampling_rate)

#plt.plot(f_deque)
# plt.plot(f)
# plt.show()

# Plot the FFT magnitude, showing only the positive half of the frequency spectrum
#plt.plot(frequencies[:len(f)], 20 * np.log10(fft_magnitude[:len(f)] / len(f)))
#plt.plot(frequencies[:len(f)], 20 * np.log10(fft_magnitude[:len(f)] / len(f)))


plt.figure(figsize=(10, 6))
# Plot the FFT in db
plt.plot(frequencies[:len(f)], 20 * np.log10(fft_magnitude[:len(f)] / len(f)))

#plt.plot(frequencies[:len(f)], fft_magnitude[:len(f)])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.title('FFT of Discrete Signal')
plt.grid()
plt.tight_layout()
#plt.show()
plt.savefig(CONFIG.output_file_prefix + "_fft.png")


# Find the peak frequency (ignoring negative frequencies)
positive_frequencies = frequencies[:len(frequencies)//2]
positive_magnitudes = fft_magnitude[:len(fft_magnitude)//2]
peak_index = np.argmax(positive_magnitudes)  # Index of max magnitude
peak_frequency = positive_frequencies[peak_index]  # Corresponding frequency

#print("peak_frequency: %d\n", peak_frequency)


# power_spectrum = (np.abs(fft_result) ** 2) / len(f)
# half_len = len(f) // 2
# frequencies = frequencies[:half_len]
# power_spectrum = power_spectrum[:half_len]
# plt.plot(frequencies, power_spectrum)
# plt.show()


plt.figure(figsize=(10, 6))
# Plot the spectrogram of lane 1 real data
#plt.specgram(f, NFFT=3000, Fs=sampling_rate, noverlap=2500, cmap='plasma')
#plt.specgram(f, NFFT=256, Fs=sampling_rate, noverlap=128, cmap='cividis')
plt.specgram(f, NFFT=256, Fs=sampling_rate, noverlap=128, cmap='inferno')
plt.title('Spectrogram of RADAR Data')
plt.xlabel('Time (seconds)')
plt.ylabel('Frequency')
#plt.ylim([0, 1000])
plt.colorbar(label='Intensity (dB)')

plt.savefig(CONFIG.output_file_prefix + "_spectrogram.png")
plt.show()


# # Compute FFT
# N = len(f)
# fft_result = np.fft.fft(f)
# frequencies = np.fft.fftfreq(N, 1/sampling_rate)  # Frequency bins

# # Compute PSD (power per Hz)
# psd = (np.abs(fft_result) ** 2) / (sampling_rate * N)

# # Keep only positive frequencies
# positive_freqs = frequencies[:N//2]
# positive_psd = psd[:N//2] * 2  # Multiply by 2 to account for negative frequencies

# # Plot
# plt.semilogy(positive_freqs, positive_psd)
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('PSD (V²/Hz)')
# plt.title('Power Spectral Density')
# plt.grid()
# plt.show()
