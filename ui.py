from dearpygui import dearpygui as dpg
import screeninfo
import threading
from measurement import perform_measurement
import sys
import os
import platform
import subprocess
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

viewport_x = (screen_width - 400) // 2
viewport_y = (screen_height - 800) // 2

ALERT_WIDTH = 350
ALERT_HEIGHT = 120
alert_pos_x = (screen_width - ALERT_WIDTH) // 2
alert_pos_y = (screen_height - ALERT_HEIGHT) // 2 - 300

# -----------------------------
#  FUNCIONES DE LA INTERFAZ
# -----------------------------
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

def open_folder(sender, app_data, user_data):
    """
    user_data recibirá el 'folder_path' que pasemos al crear el botón.
    """
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

def close_alert():
    dpg.configure_item("alert_window", show=False)

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
        args=(data, update_progress, stop_event, plot_queue),
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
    dpg.set_viewport_width(400)
    dpg.set_viewport_height(800)
    dpg.set_viewport_pos(((screen_width - 400) // 2, (screen_height - 800) // 2))
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
    new_text = f"Archivos guardados con éxito\n\nCarpeta: {folder_path}"
    
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
dpg.create_context()

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

# Creamos el theme para nuestra línea naranja
with dpg.theme() as orange_line_theme:
    # Asegúrate de usar el componente correcto, aquí mvLineSeries
    with dpg.theme_component(dpg.mvLineSeries):
        # mvPlotCol_Line define el color de la línea
        dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 127, 14, 255), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2.0, category=dpg.mvThemeCat_Plots)

with dpg.theme() as blue_line_theme:
    # Usar el componente correcto: mvPlotSeries
    with dpg.theme_component(dpg.mvLineSeries):
        # mvPlotCol_Line define el color de la línea
        dpg.add_theme_color(dpg.mvPlotCol_Line, (31, 119, 180, 255), category=dpg.mvThemeCat_Plots)
        # Establece el grosor de la línea a 2.0 píxeles
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2.0, category=dpg.mvThemeCat_Plots)

# Cargar la fuente
with dpg.font_registry():
    try:
        default_font = dpg.add_font("Roboto-Regular.ttf", 18)
        dpg.bind_font(default_font)
    except:
        print("Error al cargar la fuente 'Roboto-Regular.ttf'. Asegúrate de que el archivo existe.")
        sys.exit(1)

# -----------------------------
#  VENTANA DE CONFIGURACIÓN
# -----------------------------
with dpg.window(
    label="Configuracion",
    tag="config_window",
    width=400, height=800,
    no_move=True, no_resize=True, no_title_bar=True
):
    dpg.add_text("Configuracion", pos=(150, 40))
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=False, pos=(50, 80)):
        dpg.add_text("Identificacion")
        dpg.add_input_text(tag="identification", default_value="Identificacion 1", width=300)
        dpg.add_text("Localizacion")
        dpg.add_input_text(tag="localization", default_value="Localizacion 1", width=300)
        dpg.add_text("Activar GPS")
        dpg.add_checkbox(tag="gps", callback=toggle_gps)

        # Agrupación horizontal para Latitud y Longitud
        with dpg.group(horizontal=True, indent=0):
            # Grupo vertical para Latitud
            with dpg.group(horizontal=False):
                dpg.add_text("Latitud", tag="latitude_label", show=False)
                dpg.add_input_float(
                    tag="latitude",
                    default_value=0.0,
                    width=150,
                    show=False,
                    format="%0.8f"
                )
            
            # Grupo vertical para Longitud
            with dpg.group(horizontal=False):
                dpg.add_text("Longitud", tag="longitude_label", show=False)
                dpg.add_input_float(
                    tag="longitude",
                    default_value=0.0,
                    width=150,
                    show=False,
                    format="%0.8f"
                )

        dpg.add_spacer(height=20)
        # Agrupación horizontal para Promediaciones y Muestras
        with dpg.group(horizontal=True):
            # Grupo vertical para Promediaciones
            with dpg.group(horizontal=False):
                dpg.add_text("Promediaciones")
                dpg.add_input_int(
                    tag="averages",
                    default_value=50,
                    min_value=0,
                    max_value=100,
                    width=150,
                    step=0,
                )
            
            # Grupo vertical para Muestras
            with dpg.group(horizontal=False):
                dpg.add_text("Muestras")
                dpg.add_combo(
                    tag="number_of_samples",
                    items=[2048, 4096, 8192],
                    default_value=4096,
                    width=150
                )

        dpg.add_text("Muestreo [Hz]")
        dpg.add_combo(tag="sample_rate", items=[32000, 44100, 48000], default_value=48000, width=150)

        dpg.add_spacer(height=20)

        dpg.add_text("Distancia entre micrófonos [m]")
        dpg.add_input_float(
            tag="distance_between_mics",
            default_value=0.072, 
            width=150,
            step=0,
        )
        dpg.add_text("Distancia entre micrófono 1 y muestra [m]")
        dpg.add_input_float(
            tag="distance_between_mic_1_and_sample",
            default_value=0.5,
            width=150,
            step=0,
        )

        dpg.add_spacer(height=20)

        with dpg.group(horizontal=True, indent=0):
            with dpg.group(horizontal=False):
                dpg.add_text("Frecuencia mínima")
                dpg.add_input_int(
                    tag="freq_min",
                    default_value=500,
                    width=150,
                    step=0
                )
            
            # Grupo vertical para Longitud
            with dpg.group(horizontal=False):
                dpg.add_text("Frecuencia máxima")
                dpg.add_input_int(
                    tag="freq_max",
                    default_value=3000,
                    width=150,
                    step=0,
                )
    
    dpg.add_spacer(height=40)

    with dpg.group(horizontal=False, pos=(150, 700)):
        dpg.add_button(tag="Iniciar", label="Iniciar Medicion", callback=start_measurement)
        dpg.add_button(tag="Salir", label="Salir", callback=exit_application)

# -----------------------------
#  ALERTA MODAL
# -----------------------------
with dpg.window(
    label="Archivos Guardados",
    tag="alert_window",
    modal=True,
    show=False,
    no_title_bar=True,
    width=350,
    height=120,
    pos=(alert_pos_x, alert_pos_y),
    no_move=True
):
    dpg.add_text("", tag="alert_text")
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Volver", callback=close_alert)
        # Aquí definimos el botón con tag="open_folder_button"
        dpg.add_button(label="Ir a la carpeta", 
                       tag="open_folder_button", 
                       callback=open_folder, 
                       user_data="")  # El 'user_data' se actualizará en stop_measurement

# -----------------------------
#  VENTANA DE MEDICIÓN
# -----------------------------
with dpg.window(
    label="Medicion en Progreso",
    tag="measurement_window",
    width=screen_width,
    height=screen_height,
    no_background=False,
    no_move=True,
    no_resize=True,
    no_title_bar=True,
    show=False
):
    dpg.add_text("Medicion en Progreso", color=(255, 255, 255), tag="measurement_title")
    dpg.add_spacer(height=10)

    with dpg.group(horizontal=False):
        with dpg.group(horizontal=True, horizontal_spacing=50):

            # Recuadro: Absorción
            with dpg.child_window(width=(screen_width / 2) - 150,
                                  height=screen_height - 300,
                                  border=False,
                                  tag="absorption_box"):
                with dpg.plot(label="Coeficiente de absorción",
                              height=screen_height - 350,
                              width=(screen_width / 2) - 150,
                              tag="absorption_plot"):
                    # Eje X
                    with dpg.plot_axis(dpg.mvXAxis, label="Frecuencia (Hz)", tag="absorption_xaxis"):
                        pass
                    # Eje Y
                    with dpg.plot_axis(dpg.mvYAxis, label="Coeficiente de absorción", tag="absorption_yaxis"):
                        dpg.add_line_series([], [], label="Coeficiente de absorción",
                                            parent=dpg.last_item(), tag="absorption_series")
                        dpg.bind_item_theme("absorption_series", orange_line_theme)


            # Recuadro: Coherencia
            with dpg.child_window(width=(screen_width / 2) - 150,
                                  height=screen_height - 300,
                                  border=False,
                                  tag="coherence_box"):
                with dpg.plot(label="Coherencia",
                              height=screen_height - 350,
                              width=(screen_width / 2) - 150,
                              tag="coherence_plot"):
                    # Eje X
                    with dpg.plot_axis(dpg.mvXAxis, label="Frecuencia (Hz)", tag="coherence_xaxis"):
                        pass
                    # Eje Y
                    with dpg.plot_axis(dpg.mvYAxis, label="Coherencia", tag="coherence_yaxis"):
                        dpg.add_line_series([], [], label="Coherencia", 
                                            parent=dpg.last_item(), tag="coherence_series")
                        dpg.bind_item_theme("coherence_series", blue_line_theme)

        dpg.add_spacer(height=50)

        with dpg.group(horizontal=True, horizontal_spacing=20):
            dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=screen_width - 300)
            dpg.add_text("Progreso: 0.00% (0/0)", tag="progress_text", color=(255, 255, 255))

    dpg.add_spacer(height=30)
    dpg.add_button(tag="Detener",
                   label="Detener Medicion",
                   callback=stop_measurement,
                   width=150,
                   pos=(screen_width - 200, screen_height - 100))

# -----------------------------
#  CREAR VIEWPORT & ARRANCAR (BUCLE MANUAL)
# -----------------------------
dpg.create_viewport(title='Formulario de Configuracion', width=400, height=800, resizable=False, decorated=False)
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
