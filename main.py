import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

def get_sound_devices():
    # Device list
    return sd.query_devices()

def record_sample(n_samples, fs, device_index):
    # Record n samples with sample rate and selected device
    print("Recording...")
    recording_data = sd.rec(n_samples, samplerate=fs, channels=2, device=device_index)
    sd.wait()  # Wait to finish the recording
    print("Recording finished.")
    return recording_data

def fft(signal):
    # Get fft from signal
    return np.fft.rfft(signal)

def auto_spectrum(fft):
    # Get fft auto spectrum S_11 = A(f) * conj(Y)
    return fft * np.conjugate(fft)

def cross_spectrum(fft_1, fft_2):
    # Get fft cross spectrum S_12 = A(f) * conj(Y)
    return fft_2 * np.conjugate(fft_1)

def transfer_function(cross_spectrum, autospectrum):
    # Calculate transfer function H_12 = S12 / S11
    return cross_spectrum / autospectrum

def coherence_coefficient(S_11, S_22, S_12):
    # Calculate coherence coefficient: gamma²(f) = |S_12|² / (S_11 * S_22)
    return np.abs(S_12) / (S_11 * S_22)

def k_calculate(freqs, C, D):
    # Calculate k for every frecuency
    k_0 = 2 * np.pi * freqs / C
    k_0_prima = 1.94e-3 * np.sqrt((freqs * D) / C)
    k = k_0 - 1j * k_0_prima
    return k

def reflection_coefficient(k, S, X, L, H_12):
    # Calculate reflection coefficient: R(f) = [(H_12(f) - e^(j*k*S)) / (e^(j*k*X) - H_12(f))] * e^(j*2*k*L)
    exp_neg_jkS = np.exp(-1j * k * S)     # e^{-j(k0-k)*S} Hi_12?
    exp_jkX = np.exp(1j * k * X)          # e^{j(k0-k)*X} Hr_12?
    exp_j2kL = np.exp(1j * 2 * k * L)     # e^{j2(k0-k)*L}

    R = ((H_12 - exp_neg_jkS) / (exp_jkX - H_12)) * exp_j2kL
    return R

def absorption_coefficient(R):
    # Calculate absortion coefficient α(f) = 1 - |R(f)|²
    print("R", R.min(), R.max())
    R_mag = np.abs(R)
    print("R_mag", R_mag.min(), R_mag.max())
    R_phase = np.angle(R)
    print("R_phase", R_phase.min(), R_phase.max())

    absorption = 1 - (R_mag**2)
    return absorption

def calculate_coefficients(recording_data, n_samples, fs):
    # Input recording data channels
    in_1 = recording_data[:, 0]
    in_2 = recording_data[:, 1]

    # FFT by channel
    fft_1 = fft(in_1) # A(f)
    fft_2 = fft(in_2) # B(f)
    freqs = np.fft.rfftfreq(n_samples, 1/fs)

    # Auto Spectrums: S_11 y S_22
    S_11 = auto_spectrum(fft_1)
    S_22 = auto_spectrum(fft_2)

    # Cross Spectrum S_12
    S_12 = cross_spectrum(fft_1, fft_2)

    # Transfer function H_12:
    H_12 = transfer_function(S_12, S_11)
    # Parte real de H_12
    Hr_12 = H_12.real
    # Parte imaginaria de H_12
    Hi_12 = H_12.imag

    # Transfer function H_21:
    H_21 = transfer_function(S_12, S_22) # aun no es seguro

    # Calibration factor Hc
    Hc = calibration_factor(H_12, H_21)

    # Coherence Coefficient:
    coherence =  coherence_coefficient(S_11, S_22, S_12)
    print("coherence", coherence.min(), coherence.max())

    # K:
    k = k_calculate(freqs, C, D)

    # Reflection Coefficient:
    R = reflection_coefficient(k, S, X, L, H_12)
    
    # Absorption Coefficient:
    absorption = absorption_coefficient(R)
    print("absorption", absorption.min(), absorption.max())

    return freqs, coherence, absorption

def calibration_factor(H_12, H_21):
    # Calibration factor Hc
    return np.sqrt(H_12*H_21)

def plot_coefficients(freqs, coherence, absorption):
    # Graficar en dos subplots uno sobre otro
    plt.figure(figsize=(12, 8))  # figura más ancha y alta para apreciar mejor
    plt.subplot(2, 1, 1)
    plt.plot(freqs, coherence, label="Coherencia", color='blue')
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Coherencia [0-1]")
    plt.title("Coherencia")
    #plt.ylim([0,1])
    plt.grid(True)
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(freqs, absorption, label="Absorción", color='orange')
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Absorción [0-1]")
    plt.title("Absorción")
    #plt.ylim([0,1])
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Parameters
    fs = 48000 # Sample rate
    N = 8096 # Number of samples
    M = 1 # Number of iterations

    C = 344.0  # Sound speed in m/s (example)
    S = 0.072  # Distance between microphones (example)
    X = 0.2    # Distance between reference microphone and sample (example)
    L = 0.5    # Distance between microphones and sample (example)
    D = 0.0986 # Tube diameter (example)

    # epsilon = 1e-20
    device_index = 1
    
    sound_devices = get_sound_devices()
    print(sound_devices)

    for iteration in range(1, M):
        sample_data = record_sample(N, fs, device_index)
        freqs, coherence, absorption = calculate_coefficients(sample_data)
        plot_coefficients(freqs, coherence, absorption)