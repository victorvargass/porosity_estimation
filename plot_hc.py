import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_csv("results/hc_calibration_8192.csv")

selected_column = "hc"
# Convertir la columna 'hc' de string a números complejos
df[selected_column] = df[selected_column].apply(lambda x: complex(x))

# Obtener magnitud y fase
df["magnitude"] = np.abs(df[selected_column])
df["phase"] = np.angle(df[selected_column])

# Índices de interés
min_i = 52
max_i = 515

# Crear la figura
plt.figure(figsize=(10, 5))

# Graficar ambas curvas en el mismo gráfico
plt.plot(df["frequency"][min_i:max_i], df["magnitude"][min_i:max_i], label="Magnitud", color="b")
plt.plot(df["frequency"][min_i:max_i], df["phase"][min_i:max_i], label="Fase", color="r")

# Etiquetas y título
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Magnitud / Fase (radianes)")
plt.title("Magnitud y Fase de hc vs. Frecuencia")
plt.legend()
plt.grid()

# Ajustar límites del eje Y
plt.ylim(-0.2, 1.2)

plt.tight_layout()

results_folder = Path(f'results/HC')
results_folder.mkdir(parents=True, exist_ok=True)
plot_filename = results_folder / "plot.png"
plt.savefig(plot_filename)
plt.close()
