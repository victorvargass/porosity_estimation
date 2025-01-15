from dearpygui import dearpygui as dpg
import screeninfo
import threading
from utils import perform_measurement
import queue
from pathlib import Path

# -----------------------------
#  VARIABLES / ESTADO GLOBAL
# -----------------------------
is_measuring = False
measurement_data = {}
measurement_thread = None
stop_event = None

# Cola de datos para el gráfico
plot_queue = queue.Queue()

# -----------------------------
#  OBTENER RESOLUCIÓN DE PANTALLA
# -----------------------------
screen = screeninfo.get_monitors()[0]  # Usar el monitor principal
screen_width = screen.width
screen_height = screen.height

viewport_width = 400
viewport_height = 1000

viewport_x = (screen_width - viewport_width) // 2
viewport_y = (screen_height - viewport_height) // 2

# -----------------------------
#  FUNCIONES DE LA INTERFAZ
# -----------------------------
from ui_utils import toggle_gps, open_folder, close_alert, toggle_hc_calibration

def update_plot(sender=None, app_data=None):
    import traceback
    while not plot_queue.empty():
        try:
            data_dict = plot_queue.get_nowait()
            freqs = data_dict["freqs"]
            coherence_vals = data_dict["coherence"]
            absorption_vals = data_dict["absorption"]

            dpg.set_value("coherence_series", [freqs, coherence_vals])
            dpg.set_value("absorption_series", [freqs, absorption_vals])
        except Exception as e:
            print(f"Error al actualizar gráfico: {e}")
            traceback.print_exc()

def update_progress(iteration, total):
    if total > 0:
        progress = (iteration / total) * 100
    else:
        progress = 0

    dpg.set_value("progress_bar", progress / 100)
    dpg.set_value("progress_text", f"Progreso: {progress:.2f}% ({iteration}/{total})")

    if iteration >= total:
        stop_measurement(None, None, None)

def init_measurement(data, plot_queue):
    global measurement_thread, stop_event
    stop_event = threading.Event()

    measurement_thread = threading.Thread(
        target=perform_measurement,
        args=(data, True, update_progress, stop_event, plot_queue),
        daemon=True
    )
    measurement_thread.start()

def start_measurement(sender, app_data, user_data):
    global is_measuring, measurement_data
    is_measuring = True

    measurement_data["identification"] = dpg.get_value("identification")
    measurement_data["localization"] = dpg.get_value("localization")
    measurement_data["gps_enabled"] = dpg.get_value("gps")
    measurement_data["latitude"] = dpg.get_value("latitude") if measurement_data["gps_enabled"] else None
    measurement_data["longitude"] = dpg.get_value("longitude") if measurement_data["gps_enabled"] else None
    measurement_data["averages"] = dpg.get_value("averages")
    measurement_data["sample_rate"] = int(dpg.get_value("sample_rate"))
    measurement_data["number_of_samples"] = int(dpg.get_value("number_of_samples"))
    measurement_data["distance_between_mics"] = dpg.get_value("distance_between_mics")
    measurement_data["distance_between_mic_1_and_sample"] = dpg.get_value("distance_between_mic_1_and_sample")
    measurement_data["freq_min"] = int(dpg.get_value("freq_min"))
    measurement_data["freq_max"] = int(dpg.get_value("freq_max"))
    measurement_data["humidity_percentage"] = dpg.get_value("humidity_percentage")
    measurement_data["hc_file_path"] = dpg.get_value("hc_file_path")

    dpg.set_axis_limits("absorption_xaxis",  int(dpg.get_value("freq_min")), int(dpg.get_value("freq_max")) + 100)
    dpg.set_axis_limits("coherence_xaxis",  int(dpg.get_value("freq_min")), int(dpg.get_value("freq_max")) + 100)
    
    init_measurement(measurement_data, plot_queue)

    dpg.hide_item("config_window")

    dpg.configure_item("measurement_window", width=screen_width, height=screen_height,
                       no_move=True, no_resize=True)
    dpg.set_viewport_width(screen_width)
    dpg.set_viewport_height(screen_height)
    dpg.set_viewport_pos((0, 0))

    dpg.show_item("measurement_window")

def stop_measurement(sender, app_data, user_data):
    global is_measuring, stop_event, measurement_thread

    # Ocultar ventana de medición
    dpg.hide_item("measurement_window")
    dpg.set_viewport_width(viewport_width)
    dpg.set_viewport_height(viewport_height)
    dpg.set_viewport_pos(((screen_width - viewport_width) // 2, (screen_height - viewport_height) // 2))
    dpg.show_item("config_window")

    if is_measuring and stop_event:
        stop_event.set()
        if (measurement_thread 
            and measurement_thread.is_alive() 
            and measurement_thread != threading.current_thread()):
            measurement_thread.join()
        is_measuring = False

    # Creamos la ruta dinámica
    folder_path = f'results/{measurement_data["identification"]}/'
    abs_path = str(Path(folder_path).resolve())
    new_text = f"Archivos guardados con éxito"
    
    # Actualizamos el texto
    dpg.configure_item("alert_text", default_value=new_text)

    # IMPORTANTE: Actualizar el 'user_data' del botón para que abra la carpeta correcta
    dpg.configure_item("open_folder_button", user_data=abs_path)

    # Finalmente, mostramos la alerta
    dpg.configure_item("alert_window", show=True)

def exit_application(sender, app_data, user_data):
    global is_measuring
    if is_measuring:
        stop_measurement(sender, app_data, user_data)
    # Al usar bucle manual, forzamos salir del while (con un break o cerrando la ventana)
    dpg.stop_dearpygui()  # cierra la ventana y sale del bucle


# -----------------------------
#  CONFIGURACIÓN DE DEARPYGUI
# -----------------------------
from styles import load_styles_and_fonts

# Cargar estilos y fuentes
styles = load_styles_and_fonts()

orange_line_theme = styles["orange_line_theme"]
blue_line_theme = styles["blue_line_theme"]
green_button_theme = styles["green_button_theme"]
red_button_theme = styles["red_button_theme"]
dark_yellow_button_theme = styles["dark_yellow_button_theme"]
blue_button_theme = styles["blue_button_theme"]
default_font = styles["default_font"]
font_large = styles["font_large"]

# -----------------------------
#  VENTANA DE CONFIGURACIÓN
# -----------------------------
from config_window import create_config_window

# Crear ventana de configuración
create_config_window(
    font_large=styles["font_large"],
    window_width=viewport_width,
    window_height=viewport_height,
    green_button_theme=styles["green_button_theme"],
    red_button_theme=styles["red_button_theme"],
    start_measurement=start_measurement,  # Asegúrate de que esté definida
    exit_application=exit_application,  # Asegúrate de que esté definida
    toggle_gps=toggle_gps,  # Asegúrate de que esté definida
    toggle_hc_calibration=toggle_hc_calibration  # Asegúrate de que esté definida
)

# -----------------------------
#  ALERTA MODAL
# -----------------------------
from alert_window import create_alert_window

create_alert_window(
    open_folder=open_folder,
    close_alert=close_alert,
    green_button_theme=styles["green_button_theme"],
    dark_yellow_button_theme=styles["dark_yellow_button_theme"]
)

# -----------------------------
#  VENTANA DE MEDICIÓN
# -----------------------------
from measurement_window import create_measurement_window

create_measurement_window(
    screen_width=screen_width, 
    screen_height=screen_height, 
    orange_line_theme=styles["orange_line_theme"], 
    blue_line_theme=styles["blue_line_theme"],
    red_button_theme=styles["red_button_theme"],
    stop_measurement=stop_measurement
)

# -----------------------------
#  CREAR VIEWPORT & ARRANCAR (BUCLE MANUAL)
# -----------------------------
dpg.create_viewport(title='Configuración inicial', width=viewport_width, height=viewport_height, resizable=False, decorated=False)
dpg.setup_dearpygui()
dpg.set_viewport_pos((viewport_x, viewport_y))
dpg.show_viewport()

# En lugar de dpg.start_dearpygui(), hacemos un bucle manual:
while dpg.is_dearpygui_running():
    # 1) Actualizamos el gráfico en tiempo real.
    update_plot()

    # 2) Renderizamos un frame de Dear PyGui.
    dpg.render_dearpygui_frame()

dpg.destroy_context()
