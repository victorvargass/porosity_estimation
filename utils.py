import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
from pathlib import Path

def get_sound_devices():
    # Device list
    return sd.query_devices()

def record_sample(n_samples, fs, device_index):
    # Record n samples with sample rate and selected device
    recording_data = sd.rec(n_samples, samplerate=fs, channels=2, device=device_index)
    sd.wait()  # Wait to finish the recording
    return recording_data

def load_wav_files(channel1_file, channel2_file, number_of_samples):
    # Convert file paths to Path objects
    channel1_file = Path(channel1_file)
    channel2_file = Path(channel2_file)

    # Check that the files exist
    if not channel1_file.exists() or not channel2_file.exists():
        raise FileNotFoundError("One or both files do not exist.")

    # Read the WAV files
    fs1, channel1_data = wav.read(channel1_file)
    fs2, channel2_data = wav.read(channel2_file)

    # Verify that both files have the same sampling rate
    if fs1 != fs2:
        raise ValueError("The sampling rates of the files do not match.")

    # Verify that both files have the same length
    if len(channel1_data) != len(channel2_data):
        raise ValueError("The WAV files do not have the same number of samples.")

    # Determine the total number of segments of size number_of_samples
    num_segments = len(channel1_data) // number_of_samples

    # Trim the data so that they are divisible by number_of_samples
    channel1_data = channel1_data[:num_segments * number_of_samples]
    channel2_data = channel2_data[:num_segments * number_of_samples]

    # Split the data into segments
    channel1_segments = channel1_data.reshape(num_segments, number_of_samples)
    channel2_segments = channel2_data.reshape(num_segments, number_of_samples)

    # Create a 2-channel array: a three-dimensional array (num_segments, N, 2)
    stereo_data = np.stack((channel1_segments, channel2_segments), axis=2)
    
    # Return the stereo array and the sampling frequency
    return stereo_data, fs1

def calculate_bins(N):
    if N % 2 == 0:
        return (N // 2) + 1
    else:
        return (N + 1) // 2
    
def fft(signal):
    # Get fft from signal
    return np.fft.fft(signal)

def auto_spectrum(fft):
    # Get fft auto spectrum S_11 = A(f) * conj(Y)
    auto_spectrum = fft * np.conjugate(fft)
    return auto_spectrum

def cross_spectrum(fft_1, fft_2):
    # Get fft cross spectrum S_12 = A(f) * conj(Y)
    cross_spectrum = fft_2 * np.conj(fft_1)
    return cross_spectrum

def calculate_transfer_function(cross_spectrum, autospectrum, bins):
    # Calculate transfer function H_12 = S12 / S11
    return cross_spectrum[:bins] / autospectrum[:bins]

def calculate_coherence(S_11, S_22, S_12):
    # Calculate coherence coefficient: gamma²(f) = |S_12|² / (S_11 * S_22)
    coherence = (S_12*np.conjugate(S_12)) / (S_11*S_22)
    return coherence

def calculate_k(freqs, C):
    # Calculate k for every frecuency
    k = 2 * np.pi * freqs / C
    return k

def calculate_reflection(k, S, L, H_12):
    # Calculate reflection coefficient: R(f) = 
    HI = np.exp(-1j * k * S)
    HR = np.exp(1j * k * S)
    exp_j2kl1 = np.exp(1j * 2 * k * L)

    R = ((H_12 - HI) / (HR - H_12)) * exp_j2kl1
    return R

def calculate_absorption(R):
    # Calculate absortion coefficient α(f) = 1 - |R(f)|²
    Rmag = np.abs(R)**2
    alfa = 1 - Rmag
    return alfa

def calculate_spectrums(recording_data):
    # Input recording data channels
    in_1 = recording_data[:, 0]
    in_2 = recording_data[:, 1]

    # FFT by channel
    fft_1 = fft(in_1) # A(f)
    fft_2 = fft(in_2) # B(f)

    # Auto Spectrums: S_11 y S_22
    S_11 = auto_spectrum(fft_1)
    S_22 = auto_spectrum(fft_2)
    
    # Cross Spectrum S_12
    S_12 = cross_spectrum(fft_1, fft_2)

    return S_11, S_22, S_12

def calibration_factor(H_12, H_21):
    # Calibration factor Hc
    return np.sqrt(H_12*H_21)

def plot_signals(filename, sample_data, N, freqs, S11_aux, S22_aux, alfa, coherence):
    # Prepare figure
    plt.figure(figsize=(10,12))

    # Plot time-domain signals
    plt.subplot(3,2,1)
    plt.plot(sample_data[0][0:N])
    plt.title("Canal L")
    plt.ylim([-1,1])

    plt.subplot(3,2,2)
    plt.plot(sample_data[0][0:N])
    plt.title("Canal R")
    plt.ylim([-1,1])
    
    # Plot initial S11 and S22
    plt.subplot(3,2,3)
    plt.plot(freqs[0:400], S11_aux[0:400].real)  # Real part since it's power
    plt.title("S11 avg")
    plt.ylim([0,100000])

    plt.subplot(3,2,4)
    plt.plot(freqs[0:400], S22_aux[0:400].real)
    plt.title("S22 avg")
    plt.ylim([0,100000])

    plt.subplot(3,2,5)
    plt.plot(freqs[0:400], alfa[0:400].real)  # alfa is real
    plt.title("Coef. Absorcion")
    plt.ylim([0,1])

    plt.subplot(3,2,6)
    plt.plot(freqs[0:400], coherence[0:400].real)  # coh should be real and >=0
    plt.title("Coherencia")
    plt.ylim([0,1])

    plt.tight_layout()
    plots_folder = Path('plots/')
    plots_folder.mkdir(parents=True, exist_ok=True)
    plot_filename = plots_folder / f"{filename}.png"
    plt.savefig(plot_filename)
    plt.show()


def generate_csv(freqs, S11_aux, S12_aux, S22_aux, R, alfa, H_12, coherence, filename):

    # Magnitud y fase de S12 y H12
    S12_mag = np.abs(S12_aux)
    S12_phase = np.angle(S12_aux)
    H12_mag = np.abs(H_12)
    H12_phase = np.angle(H_12)
    
    R_mag = np.abs(R)
    
    S11_aux = S11_aux[:len(freqs)]
    S12_mag = S12_mag[:len(freqs)]
    S12_phase = S12_phase[:len(freqs)]
    S22_aux = S22_aux[:len(freqs)]
    coherence = coherence[:len(freqs)]

    data = {
        "f": freqs.astype(int),
        "S11": np.round(S11_aux.real, 2),
        "S12 mag": np.round(S12_mag, 2),
        "S12 Fase": np.round(S12_phase, 2),
        "S22": np.round(S22_aux.real, 2),
        "R mag": np.round(R_mag, 2),
        "Alfa": np.round(alfa, 2),
        "H12 mag": np.round(H12_mag, 2),
        "H12 fase": np.round(H12_phase, 2),
        "Coherencia": np.round(coherence.real, 2)
    }
    
    df = pd.DataFrame(data)

    data_folder = Path('data/')
    data_folder.mkdir(parents=True, exist_ok=True)
    data_filename = data_folder / f"{filename}.csv"
    df.to_csv(data_filename, index=False)
    print(f"Archivo CSV generado: {filename}")