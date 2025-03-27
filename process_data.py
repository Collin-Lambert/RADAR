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


def compute_spectrogram_and_max_freq(signal, sampling_rate, nfft=1024, noverlap=512):
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
    signal = signal / np.max(signal)


    # Compute spectrogram
    freqs, times, Sxx = spectrogram(signal, fs=sampling_rate, nperseg=nfft, noverlap=noverlap, return_onesided=False)

    # Shift frequencies to center zero frequency
    freqs = np.fft.fftshift(freqs)
    Sxx = np.fft.fftshift(Sxx, axes=0)

    # Convert power to dB
    Sxx_dB = 10 * np.log10(Sxx + 1e-10)  # Add small value to avoid log(0)

    # Find dominant frequency at each time step
    max_freq_indices = np.argmax(Sxx, axis=0)  # Find index of max power in each time step
    max_powers = Sxx_dB[max_freq_indices, np.arange(len(times))]  # Get corresponding power values

    # find the max of max_powers
    max_max_powers = max(max_powers)
    power_threshold = max_max_powers - 5
    print(f"power_threshold: {power_threshold}")

    # Apply threshold: If max power < threshold, set frequency to 0
    max_freqs = freqs[max_freq_indices] * (max_powers > power_threshold)

    # Plot the spectrogram
    # plt.figure(figsize=(10, 6))
    # plt.pcolormesh(times, freqs, Sxx_dB, shading='auto', cmap='inferno')
    # plt.colorbar(label='Power (dB)')
    # plt.xlabel("Time (s)")
    # plt.ylabel("Frequency (Hz)")
    # plt.title("Spectrogram")
    # plt.show()

    return freqs, times, Sxx, max_freqs


# do stuff

def process_data(display_spectrogram=True):
    decimation = CONFIG.decimation

    # Sampling rate in Hz
    sampling_rate = 6e6 / decimation  # 4 million samples per second

    f_prime = np.fromfile(open(CONFIG.file_name), dtype=np.complex64)
    f_high = highpass_chebyshev(f_prime, CONFIG.high_pass_cutoff, 6e6)
    f = lowpass_filter_decimate(f_high, 1.5e6/decimation, 6e6, decimation, 6)

    freqs, times, Sxx, max_freqs = compute_spectrogram_and_max_freq(f, sampling_rate, CONFIG.fft_size, CONFIG.fft_overlap)

    #plt.plot(max_freqs)

    velocities = (max_freqs * c) / (2 * 85e9 + max_freqs)

    # plt.figure(figsize=(10, 6))
    # plt.plot(velocities)
    # plt.tight_layout()
    # plt.show()

    print(f"max velocity: {max(abs(velocities))}")

    # Perform FFT
    fft_result = np.fft.fft(f)
    fft_magnitude = np.abs(fft_result)

    # Calculate frequency bins
    frequencies = np.fft.fftfreq(len(f), 1 / sampling_rate)


    # plt.figure(figsize=(10, 6))
    # # Plot the FFT in db
    # plt.plot(frequencies[:len(f)], 20 * np.log10(fft_magnitude[:len(f)] / len(f)))

    # #plt.plot(frequencies[:len(f)], fft_magnitude[:len(f)])
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Magnitude (dB)')
    # plt.title('FFT of Discrete Signal')
    # plt.grid()
    # plt.tight_layout()
    # plt.show()
    # plt.savefig(CONFIG.output_file_prefix + "_fft.png")

    plt.figure(figsize=(10, 6))
    # Plot the spectrogram of lane 1 real data
    #plt.specgram(f, NFFT=3000, Fs=sampling_rate, noverlap=2500, cmap='plasma')
    #plt.specgram(f, NFFT=256, Fs=sampling_rate, noverlap=128, cmap='cividis')
    plt.specgram(f, NFFT=CONFIG.fft_size, Fs=sampling_rate, noverlap=CONFIG.fft_overlap, cmap='inferno')
    plt.title('Spectrogram of RADAR Data')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.colorbar(label='Intensity (dB)')

    plt.tight_layout()

    if (display_spectrogram):
        plt.show()


    # plt.tight_layout()
    # #plt.show()
    # # plt.savefig(CONFIG.output_file_prefix + "_spectrogram.png")

    # fig, ax = plt.subplots(figsize=(5, 2.5))
    # ax.specgram(f, NFFT=CONFIG.fft_size, Fs=sampling_rate, noverlap=CONFIG.fft_overlap, cmap='inferno')
    # ax.set_axis_off()  # Remove axis
    # fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # Remove white border
    # fig.colorbar(ax.images[0], ax=ax, label='Intensity (dB)')


    # fig.tight_layout()
    # #plt.show()
    # return fig
    return max(abs(velocities)) # return max velocity



if __name__ == "__main__":
    process_data()

