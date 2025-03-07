import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import scipy.io.wavfile as wav
from pathlib import Path
import time
matplotlib.use("Agg")  # Backend "offscreen", sin GUI

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
    auto_spectrum = np.abs(fft) ** 2
    return auto_spectrum

def cross_spectrum(fft_1, fft_2):
    # Get fft cross spectrum S_12 = A(f) * conj(Y)
    cross_spectrum = fft_2 * np.conj(fft_1)
    return cross_spectrum

def calculate_transfer_function(cross_spectrum, autospectrum, bins, hc_file_path=None):
    # Calculate transfer function H_12 = S12 / S11
    H12 = cross_spectrum[:bins] / autospectrum[:bins]
    if hc_file_path:
        df = pd.read_csv(hc_file_path)
        hc_column = df['hc']
        HC = np.array([complex(x) for x in hc_column])
        H12 = H12 / HC
    return H12

def calculate_coherence(S_11, S_22, S_12):
    # Calculate coherence coefficient: gamma²(f) = |S_12|² / (S_11 * S_22)
    coherence = np.abs(S_12)**2 / (S_11 * S_22 + 1e-10)
    return coherence.real

def calculate_k(freqs, C):
    # Calculate k for every frecuency
    k = (2 * np.pi * freqs) / C
    return k

def calculate_reflection(k, S, L, H_12):
    # Calculate reflection coefficient: R(f) = 
    HI = np.exp(-1j * k * S)
    HR = np.exp(1j * k * S)
    exp_j2kl1 = np.exp(1j * 2 * k * L)

    denominator = HR - H_12 + 1e-10  # Factor de seguridad
    R = ((H_12 - HI) / denominator) * exp_j2kl1
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

    return S_11, S_22, S_12, fft_1, fft_2, in_1, in_2


def calibration_factor(h12_I, h12_II, freqs):
    h12_I_squared = h12_I**2
    h12_II_squared = h12_II**2
    
    hc = np.sqrt(h12_I_squared / h12_II_squared)

    hc_data = {
        "frequency":  freqs,
        "hc":  hc,
    }

    return hc_data


def plot_signals(filename, freqs, alfa, coherence, freq_min, freq_max):
    # Verificar que los tamaños de freqs, alfa y coherence coincidan
    min_length = min(len(freqs), len(alfa), len(coherence))
    freqs = freqs[:min_length]
    alfa = alfa[:min_length]
    coherence = coherence[:min_length]

    # Filtrar índices según los límites de frecuencia
    mask = (freqs >= freq_min) & (freqs <= freq_max)

    # Filtrar los datos para las frecuencias seleccionadas
    freqs_filtered = freqs[mask]
    alfa_filtered = alfa[mask]
    coherence_filtered = coherence[mask]

    # Crear un solo gráfico con dos curvas
    plt.figure(figsize=(10, 6))
    plt.plot(freqs_filtered, alfa_filtered.real, label="Coeficiente de absorción", color="blue")
    plt.plot(freqs_filtered, coherence_filtered.real, label="Coherencia", color="red")

    # Títulos y etiquetas
    plt.title("Coeficiente de absorción y Coherencia")
    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Valor")
    plt.legend()
    plt.ylim([0, 1])
    plt.grid(True)


    results_folder = Path(f'results/{filename}/')
    results_folder.mkdir(parents=True, exist_ok=True)
    plot_filename = results_folder / "plot.png"
    plt.savefig(plot_filename)
    plt.close()

def generate_csv(freqs, freq_min, freq_max, S11_aux, S12_aux, S22_aux, R, alfa, H_12, coherence, filename):

    mask_freqs = (freqs >= freq_min) & (freqs <= freq_max)
    # Magnitud y fase de S12 y H12
    S12_mag = np.abs(S12_aux)
    S12_phase = np.angle(S12_aux)
    H12_mag = np.abs(H_12)
    H12_phase = np.angle(H_12)
    R_mag = np.abs(R)
    R_phase = np.angle(R)

    S11_aux = S11_aux[:len(freqs)]
    S12_mag = S12_mag[:len(freqs)]
    S12_phase = S12_phase[:len(freqs)]
    S22_aux = S22_aux[:len(freqs)]
    R_mag = R_mag[:len(freqs)]
    R_phase = R_phase[:len(freqs)]
    alfa = alfa[:len(freqs)]
    H12_mag = H12_mag[:len(freqs)]
    H12_phase = H12_phase[:len(freqs)]
    coherence = coherence[:len(freqs)]

    freqs_filtered = freqs[mask_freqs]
    S11_aux_filtered = S11_aux[mask_freqs]
    S12_mag_filtered = S12_mag[mask_freqs]
    S12_phase_filtered = S12_phase[mask_freqs]
    S22_aux_filtered = S22_aux[mask_freqs]
    R_mag_filtered = R_mag[mask_freqs]
    R_phase_filtered = R_phase[mask_freqs]
    alfa_filtered = alfa[mask_freqs]
    H12_mag_filtered = H12_mag[mask_freqs]
    H12_phase_filtered = H12_phase[mask_freqs]
    coherence_filtered = coherence[mask_freqs]

    data = {
        "frequency": freqs_filtered.astype(int),
        "s11": np.round(S11_aux_filtered.real, 4),
        "s12_mag": np.round(S12_mag_filtered, 4),
        "s12_phase": np.round(S12_phase_filtered, 4),
        "s22": np.round(S22_aux_filtered.real, 4),
        "r_mag": np.round(R_mag_filtered, 3),
        "r_phase": np.round(R_phase_filtered, 3),
        "alfa": np.round(alfa_filtered, 2),
        "coherence": np.round(coherence_filtered.real, 2)
    }
    
    df = pd.DataFrame(data)

    data_folder = Path('data/')
    data_folder.mkdir(parents=True, exist_ok=True)
    data_filename = data_folder / f"{filename}.csv"
    df.to_csv(data_filename, index=False)
    print(f"Archivo CSV generado: {filename}")


def generate_short_csv(freqs, humidity_percentage, alfa, coherence, filename, freq_min, freq_max):
    # Crear máscara para las frecuencias dentro del rango
    mask_freqs = (freqs >= freq_min) & (freqs <= freq_max)

    # Ajustar las longitudes de alfa y coherence si no coinciden con freqs
    alfa = alfa[:len(freqs)]
    coherence = coherence[:len(freqs)]

    # Filtrar los datos según la máscara
    freqs_filtered = freqs[mask_freqs]
    alfa_filtered = alfa[mask_freqs]
    coherence_filtered = coherence[mask_freqs]

    # Preparar datos para exportar
    rows = len(freqs_filtered)  # Número total de filas
    data = {
        "humidity_percentage": [humidity_percentage] + [None] * (rows - 1),
        "frequency": freqs_filtered.astype(int),
        "alfa": np.round(alfa_filtered, 2),
        "coherence": np.round(coherence_filtered.real, 2)
    }

    df = pd.DataFrame(data)

    # Crear carpeta y guardar archivo CSV
    results_folder = Path(f'results/{filename}/')
    results_folder.mkdir(parents=True, exist_ok=True)
    data_filename = results_folder / "data.csv"
    df.to_csv(data_filename, index=False)


def perform_measurement(data, is_sample=False, update_progress_callback=None, stop_event=None, plot_queue=None):
    """
    Ejecuta el proceso de medición.
    Recibe la cola 'plot_queue' para enviar datos de gráficos a ui.py.
    """
    fs = data.get('sample_rate', 48000)
    N = data.get('number_of_samples', 8192)
    bins = calculate_bins(N)
    M = data.get('averages', 50)

    C = 340.0
    S = data.get('distance_between_mics', 0.0315)
    L = data.get('distance_between_mic_1_and_sample', 0.1115)
    D = 0.0986

    freq_min = data.get('freq_min', 500)
    freq_max = data.get('freq_max', 3000)
    
    humidity_percentage = round(data.get('humidity_percentage', 0.0), 2)
    hc_file_path = data.get('hc_file_path', "")

    device_index = 1

    if is_sample:
        samples_folder = Path('samples/')
        channel1_file = samples_folder / 'CalH12 - CH1.wav'
        channel2_file = samples_folder / 'CalH12 - CH2.wav'
        filename = data.get('identification', "CalH12")
        sample_data, fs = load_wav_files(channel1_file, channel2_file, N)
    else:
        filename = data.get('identification', "identification")

    freqs = fs * np.arange(bins) / N
    k = calculate_k(freqs, C)

    # Acumuladores
    S11_aux = S22_aux = S12_aux = np.zeros((N,))
    coherence = None
    R = None
    alfa = None

    for iteration in range(1, M + 1):
        if stop_event and stop_event.is_set():
            print("Medición detenida por el usuario.")
            break

        # Tomamos la parte 'iteration-1' del sample_data si is_sample
        if is_sample:
            S_11, S_22, S_12, fft_1, fft_2, in_1, in_2 = calculate_spectrums(sample_data[iteration-1])
        else:
            sd = record_sample(N, fs, device_index)
            S_11, S_22, S_12, fft_1, fft_2, in_1, in_2 = calculate_spectrums(sd)

        # Promedio acumulativo
        S11_sum = S_11 + (iteration-1)*S11_aux
        S22_sum = S_22 + (iteration-1)*S22_aux
        S12_sum = S_12 + (iteration-1)*S12_aux

        S11_avg = S11_sum / iteration
        S22_avg = S22_sum / iteration
        S12_avg = S12_sum / iteration

        # Coherencia
        coherence = calculate_coherence(S11_aux, S22_aux, S12_aux)
        # Transfer function
        H_12 = calculate_transfer_function(S12_aux, S11_aux, bins, hc_file_path)
        # Reflection
        R = calculate_reflection(k, S, L, H_12)

        # Absorption
        alfa = calculate_absorption(R)

        # Simulamos un retardo
        time.sleep(0.1)

        # Llamar callback de progreso
        if update_progress_callback:
            update_progress_callback(iteration, M)

        # Enviar datos a la cola para gráficos
        if plot_queue is not None:
            try:
                plot_queue.put({
                    "freqs": freqs.tolist(),
                    "coherence": coherence.tolist() if coherence is not None else [],
                    "absorption": alfa.tolist() if alfa is not None else []
                })
            except Exception as e:
                print(f"No se pudo encolar datos de gráficos: {e}")
    
        S11_aux = S11_avg
        S22_aux = S22_avg
        S12_aux = S12_avg


    plot_signals(
        filename=filename,
        freqs=freqs,
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max
    )
    # Al terminar, generamos CSV
    generate_short_csv(
        filename=filename,
        freqs=freqs,
        humidity_percentage=humidity_percentage,
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max,
    )


def perform_calibration(fs, N, M, channel, is_sample=False):

    # Parameters
    bins = calculate_bins(N)
    C = 340.0  # Sound speed in m/s (m)

    #sound_devices = get_sound_devices()
    #print(sound_devices)
    device_index = 1

    if is_sample:
        samples_folder = Path('samples/')
        if channel == 1:
            channel1_file = samples_folder / 'CalH12 - CH1.wav'
            channel2_file = samples_folder / 'CalH12 - CH2.wav'
        if channel == 2:
            channel1_file = samples_folder / 'CalH21 - CH2.wav'
            channel2_file = samples_folder / 'CalH21 - CH1.wav'
        sample_data, fs = load_wav_files(channel1_file, channel2_file, N) # Cut the sample in N size splits

    freqs = fs * np.arange(bins) / N
    k = calculate_k(freqs, C)

    S11_aux = S22_aux = S12_aux = np.zeros((N,))

    for iteration in range(1, M + 1):
        if is_sample:
            S_11, S_22, S_12, fft_1, fft_2, in_1, in_2 = calculate_spectrums(sample_data[iteration-1])
        else:
            sample_data = record_sample(N, fs, device_index)
            S_11, S_22, S_12, fft_1, fft_2, in_1, in_2 = calculate_spectrums(sample_data)

        S11_sum = S_11 + (iteration-1)*S11_aux
        S22_sum = S_22 + (iteration-1)*S22_aux
        S12_sum = S_12 + (iteration-1)*S12_aux

        S11_avg = S11_sum / iteration
        S22_avg = S22_sum / iteration
        S12_avg = S12_sum / iteration

        S11_aux = S11_avg
        S22_aux = S22_avg
        S12_aux = S12_avg

        # Transfer function H_12:
        H_12 = calculate_transfer_function(S12_aux, S11_aux, bins)
        print(iteration)
    return H_12, freqs
