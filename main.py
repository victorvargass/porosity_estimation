
from utils import calculate_bins, load_wav_files, record_sample, get_sound_devices, calculate_k, calculate_spectrums, calculate_coherence, calculate_transfer_function, calculate_reflection, calculate_absorption, plot_signals, generate_csv, generate_short_csv
from pathlib import Path
import numpy as np

if __name__ == "__main__":
    # Parameters
    fs = 48000 # Sample rate
    N = 8192 # Number of samples
    bins = calculate_bins(N)
    M = 50 # Number of iterations

    C = 340.0  # Sound speed in m/s (m)
    S = 0.072  # Distance between microphones (m)
    L = 0.5    # Distance between reference microphone and sample (m)
    D = 0.0986 # Tube diameter (m)

    freq_min, freq_max = 250, 2000
    y_min, y_max = 0, 1

    is_sample = True

    #sound_devices = get_sound_devices()
    #print(sound_devices)
    device_index = 1

    if is_sample:
        samples_folder = Path('samples/')
        channel1_file = samples_folder / 'Take1_Audio 1-1.wav'
        channel2_file = samples_folder / 'Take1_Audio 2-1.wav'
        filename = 'Muestra 1'
        sample_data, fs = load_wav_files(channel1_file, channel2_file, N) # Cut the sample in N size splits 

    freqs = fs * np.arange(bins) / N
    k = calculate_k(freqs, C)

    S11_aux = S22_aux = S12_aux = np.zeros((N,))

    for iteration in range(1, M + 1):
        print(f"Iteración {iteration} iniciada")
        if is_sample:
            S_11, S_22, S_12 = calculate_spectrums(sample_data[iteration-1])
        else:
            sample_data = record_sample(N, fs, device_index)
            S_11, S_22, S_12 = calculate_spectrums(sample_data)

        S11_sum = S_11 + (iteration-1)*S11_aux
        S22_sum = S_22 + (iteration-1)*S22_aux
        S12_sum = S_12 + (iteration-1)*S12_aux

        S11_avg = S11_sum / iteration
        S22_avg = S22_sum / iteration
        S12_avg = S12_sum / iteration

        S11_aux = S11_avg
        S22_aux = S22_avg
        S12_aux = S12_avg


        # Coherence Coefficient:
        coherence =  calculate_coherence(S11_aux, S22_aux, S12_aux)

        # Transfer function H_12:
        H_12 = calculate_transfer_function(S12_aux, S11_aux, bins)

        # Reflection Coefficient:
        R = calculate_reflection(k, S, L, H_12)
        
        # Absorption Coefficient:
        alfa = calculate_absorption(R)

        print(f"Iteración {iteration} finalizada")

    plot_signals(
        filename=filename,
        freqs=freqs,
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max
    )
    generate_short_csv(
        filename=filename,
        freqs=freqs,
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max,
    )

    '''
    # Generar el archivo CSV
    generate_csv(
        filename=filename,
        freqs=freqs,
        S11_aux=S11_aux,
        S12_aux=S12_aux,
        S22_aux=S22_aux,
        R=R,
        alfa=alfa,
        H_12=H_12,
        coherence=coherence
    )
    '''