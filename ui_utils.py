import dearpygui.dearpygui as dpg
import os
import platform
import subprocess

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

