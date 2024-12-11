import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

# Lista de dispositivos
print(sd.query_devices())

# Parámetros
fs = 48000 # Frecuencia de muestreo
N = 8096 # Número de muestras
M = 50 # Número de promediaciones

C = 344.0  # Velocidad del sonido en m/s (ejemplo)
S = 0.072    # Distancia entre micrófonos (ejemplo)
X = 0.2    # Distancia entre micrófono de referencia y la muestra (ejemplo)
L = 0.5    # Distancia desde micrófonos a la muestra (ejemplo)
D = 0.0986    # Diámetro del tubo (ejemplo)

epsilon = 1e-20 # Para asegurarse de evitar division por cero

# Grabar N muestras de 2 canales
print("Grabando...")
data = sd.rec(N, samplerate=fs, channels=2, device=1)
sd.wait()  # Esperar a que termine la grabación
print("Grabación finalizada.")

# Canales de entrada
in_1 = data[:, 0]
in_2 = data[:, 1]

# FFT por canal
fft_1 = np.fft.rfft(in_1) # A(f)
fft_2 = np.fft.rfft(in_2) # B(f)
freqs = np.fft.rfftfreq(N, 1/fs)

# Autoespectros: S11 y S22
S_11 = fft_1 * np.conjugate(fft_1)
S_22 = fft_2 * np.conjugate(fft_2)

# Espectro cruzado: S_12 = A(f) * conj(Y)
S_12 = fft_2 * np.conjugate(fft_1)

# Función de transferencia:
H_12 = S_12 / S_11
H_21 = S_12 / S_22 # aun no es seguro

# Calibración factor Hc
HC = np.sqrt(H_12*H_21)

# Coeficiente de coherencia: gamma²(f) = |S_12|² / (S_11 * S_22)
coherence = np.abs(S_12) / (S_11 * S_22)

# Cálculo de k para cada frecuencia
k_0 = 2 * np.pi * freqs / C
k_0_prima = 1.94e-3 * np.sqrt((freqs * D) / C)

k = k_0 - 1j * k_0_prima

# Coeficiente de reflexión: R(f) = [(H_12(f) - e^(j*k*S)) / (e^(j*k*X) - H_12(f))] * e^(j*2*k*L)
exp_neg_jkS = np.exp(-1j * k * S)     # e^{-j(k0-k)*S}
exp_jkX = np.exp(1j * k * X)          # e^{j(k0-k)*X}
exp_j2kL = np.exp(1j * 2 * k * L)     # e^{j2(k0-k)*L}

R = ((H_12 - exp_neg_jkS) / (exp_jkX - H_12 + epsilon)) * exp_j2kL

# Ahora R es un array complejo, el coeficiente de reflexión frecuencia a frecuencia.
# Puedes obtener su magnitud y fase si lo deseas:
print("R", R.min(), R.max())
R_mag = np.abs(R)
print("R_mag", R_mag.min(), R_mag.max())
R_phase = np.angle(R)

# Coeficiente de absorción: α(f) = 1 - |R(f)|²
absorption = 1 - (R_mag**2)

print("coherence", coherence.min(), coherence.max())
print("absorption", absorption.min(), absorption.max())

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


def reflection_coefficient():
    return

def absorption_coefficient():
    return

def calibration():
    return

def plot():
    return

