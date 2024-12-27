from pathlib import Path
import numpy as np
import time

from utils import (
    calculate_bins, load_wav_files, record_sample, get_sound_devices, 
    calculate_k, calculate_spectrums, calculate_coherence, 
    calculate_transfer_function, calculate_reflection, 
    calculate_absorption, plot_signals, generate_csv, generate_short_csv
)

def perform_measurement(data, update_progress_callback=None, stop_event=None, plot_queue=None):
    """
    Ejecuta el proceso de medición.
    Recibe la cola 'plot_queue' para enviar datos de gráficos a ui.py.
    """
    fs = data.get('sample_rate', 48000)
    N = data.get('number_of_samples', 8192)
    bins = calculate_bins(N)
    M = data.get('averages', 50)

    C = 340.0
    S = data.get('distance_between_mics', 0.072)
    L = data.get('distance_between_mic_1_and_sample', 0.5)
    D = 0.0986

    freq_min = data.get('freq_min', 500)
    freq_max = data.get('freq_max', 3000)

    is_sample = True
    device_index = 1

    if is_sample:
        samples_folder = Path('samples/')
        channel1_file = samples_folder / 'Take1_Audio 1-1.wav'
        channel2_file = samples_folder / 'Take1_Audio 2-1.wav'
        filename = data.get('identification', "identification")
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
            S_11, S_22, S_12 = calculate_spectrums(sample_data[iteration-1])
        else:
            sd = record_sample(N, fs, device_index)
            S_11, S_22, S_12 = calculate_spectrums(sd)

        # Promedio acumulativo
        S11_sum = S_11 + (iteration-1)*S11_aux
        S22_sum = S_22 + (iteration-1)*S22_aux
        S12_sum = S_12 + (iteration-1)*S12_aux

        S11_avg = S11_sum / iteration
        S22_avg = S22_sum / iteration
        S12_avg = S12_sum / iteration

        S11_aux = S11_avg
        S22_aux = S22_avg
        S12_aux = S12_avg

        # Coherencia
        coherence = calculate_coherence(S11_aux, S22_aux, S12_aux)
        # Transfer function
        H_12 = calculate_transfer_function(S12_aux, S11_aux, bins)
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
        alfa=alfa,
        coherence=coherence,
        freq_min=freq_min,
        freq_max=freq_max,
    )
