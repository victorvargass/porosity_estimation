import dearpygui.dearpygui as dpg
import os
import platform
import subprocess
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# Alternar GPS
def toggle_gps(sender, app_data, user_data):
    if dpg.get_value("gps"):
        dpg.show_item("latitude_label")
        dpg.show_item("latitude")
        dpg.show_item("longitude_label")
        dpg.show_item("longitude")
        dpg.set_value("latitude", -39.8384882)
        dpg.set_value("longitude", -73.2175568)
        dpg.configure_item("latitude", enabled=False, format="%0.8f", step=0, step_fast=0)
        dpg.configure_item("longitude", enabled=False, format="%0.8f", step=0, step_fast=0)
    else:
        dpg.hide_item("latitude_label")
        dpg.hide_item("latitude")
        dpg.hide_item("longitude_label")
        dpg.hide_item("longitude")

def toggle_hc_calibration(sender, app_data, user_data):
    if dpg.get_value("hc_calibration"):
        dpg.show_item("hc_file")
    else:
        dpg.hide_item("hc_file")
        dpg.set_value("hc_file_path", "")
        dpg.set_value("selected_file_text", "No se ha seleccionado ningún archivo.")

# Abrir la carpeta de resultados
def open_folder(sender, app_data, user_data):
    folder_path = user_data
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(folder_path)
        elif system == "Darwin":
            subprocess.call(["open", folder_path])
        else:
            subprocess.call(["xdg-open", folder_path])
    except Exception as e:
        print(f"No se pudo abrir la carpeta: {e}")

# Cerrar ventana de alerta
def close_alert():
    dpg.configure_item("alert_window", show=False)

def validate_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        calibration_hc_n = (df.shape[0] - 1 ) * 2
        number_of_samples = int(dpg.get_value("number_of_samples"))
        # Ejemplo de validaciones:
        # 1. Verificar si contiene ciertas columnas
        required_columns = {"frequency", "hc"}
        if not required_columns.issubset(df.columns):
            dpg.set_value("hc_file_path", "")
            dpg.set_value("selected_file_text", "Error: Faltan columnas requeridas.")
            return False
        # 2. Verificar si contiene ciertas columnas
        if not calibration_hc_n == number_of_samples:
            dpg.set_value("selected_file_text", "Error: Debe ser compatible con el número de muestras.")
            return False
        dpg.set_value("hc_file_path", file_path)
        dpg.set_value("selected_file_text", f"Archivo: {file_path.split('/')[-1]}")
        return True

    except Exception as e:
        print(f"Error al leer o validar el archivo CSV: {e}")
        return False

def select_file_with_native_dialog():
    # Ocultar la ventana principal de Tkinter
    root = tk.Tk()
    root.withdraw()

    # Abrir el diálogo de selección de archivo
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
    )

    # Mostrar el archivo seleccionado en Dear PyGui
    if file_path:
        validate_csv_file(file_path)

def on_number_of_samples_update(sender, app_data):
    print(dpg.get_value("hc_file_path"))
    if dpg.get_value("hc_file_path"):
        dpg.set_value("hc_file_path", "")
        dpg.set_value("selected_file_text", "Error: Debe ser compatible con el número de muestras.")