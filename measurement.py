# measurement.py
from pathlib import Path
import numpy as np
import time
from utils import (
    calculate_bins, load_wav_files, record_sample, get_sound_devices, 
    calculate_k, calculate_spectrums, calculate_coherence, 
    calculate_transfer_function, calculate_reflection, 
    calculate_absorption, plot_signals, generate_csv, generate_short_csv
)

def perform_measurement(data, update_progress_callback=None, stop_event=None):
    """
    Ejecuta el proceso de medición.

    :param data: Diccionario con los datos de configuración de la medición.
    :param update_progress_callback: Función callback para actualizar el progreso en la GUI.
    :param stop_event: Evento para detener la medición desde la GUI.
    """
    # Parámetros
    fs = data.get('sample_rate', 48000)  # Sample rate
    N = data.get('number_of_samples', 8192)   # Number of samples
    bins = calculate_bins(N)
    M = data.get('averages', 50)  # Number of iterations

    C = 340.0  # Sound speed in m/s
    S = 0.072  # Distance between microphones in meters
    L = 0.5    # Distance between reference microphone and sample in meters
    D = 0.0986 # Tube diameter in meters

    freq_min, freq_max = 250, 2000
    y_min, y_max = 0, 1

    is_sample = True

    device_index = 1  # Índice del dispositivo de sonido

    if is_sample:
        samples_folder = Path('samples/')
        channel1_file = samples_folder / 'Take1_Audio 1-1.wav'
        channel2_file = samples_folder / 'Take1_Audio 2-1.wav'
        filename = 'Muestra 1'
        sample_data, fs = load_wav_files(channel1_file, channel2_file, N)  # Corta la muestra en fragmentos de tamaño N

    freqs = fs * np.arange(bins) / N
    k = calculate_k(freqs, C)

    S11_aux = S22_aux = S12_aux = np.zeros((N,))

    coherence = None
    H_12 = None
    R = None
    alfa = None

    for iteration in range(1, M + 1):
        if stop_event and stop_event.is_set():
            print("Medición detenida por el usuario.")
            break

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
        coherence = calculate_coherence(S11_aux, S22_aux, S12_aux)

        # Transfer function H_12:
        H_12 = calculate_transfer_function(S12_aux, S11_aux, bins)

        # Reflection Coefficient:
        R = calculate_reflection(k, S, L, H_12)
        
        # Absorption Coefficient:
        alfa = calculate_absorption(R)

        time.sleep(0.1)
        print(f"Iteración {iteration} finalizada")

        # Actualizar el progreso en la GUI
        if update_progress_callback:
            update_progress_callback(iteration, M, alfa, coherence)

    generate_short_csv(
        filename=filename,
        freqs=freqs,
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max,
    )
    print("Medición completada.")
