# ui.py
from dearpygui import dearpygui as dpg
import screeninfo
import threading
from measurement import perform_measurement
import sys
import os
import platform
import subprocess

# Variables globales
is_measuring = False
measurement_data = {}
measurement_thread = None
stop_event = None


# Obtener la resolución de la pantalla
screen = screeninfo.get_monitors()[0]  # Usar el monitor principal
screen_width = screen.width
screen_height = screen.height

# Centrar el viewport en la pantalla
viewport_x = (screen_width - 400) // 2
viewport_y = (screen_height - 700) // 2

ALERT_WIDTH = 350
ALERT_HEIGHT = 120

alert_pos_x = (screen_width - ALERT_WIDTH) // 2
alert_pos_y = (screen_height - ALERT_HEIGHT) // 2 - 300

def open_folder():
    """Abre la carpeta inventada según el sistema operativo."""
    folder_path = "C:/ruta/inventada"  # Ajusta o inventa la ruta que quieras
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(folder_path)
        elif system == "Darwin":  # macOS
            subprocess.call(["open", folder_path])
        else:  # Linux y otros
            subprocess.call(["xdg-open", folder_path])
    except Exception as e:
        print(f"No se pudo abrir la carpeta: {e}")

def close_alert():
    """Función que cierra la ventana de alerta 'alert_window'."""
    dpg.configure_item("alert_window", show=False)

def toggle_gps(sender, app_data, user_data):
    if dpg.get_value("GPS"):
        # Mostrar campos de latitud y longitud y asignar valores simulados
        dpg.show_item("Latitud_Label")
        dpg.show_item("Latitud")
        dpg.show_item("Longitud_Label")
        dpg.show_item("Longitud")
        dpg.set_value("Latitud", -39.8384882)
        dpg.set_value("Longitud", -73.2175568)
        dpg.configure_item("Latitud", enabled=False, format="%0.8f", step=0, step_fast=0)
        dpg.configure_item("Longitud", enabled=False, format="%0.8f", step=0, step_fast=0)
    else:
        # Ocultar campos de latitud y longitud
        dpg.hide_item("Latitud_Label")
        dpg.hide_item("Latitud")
        dpg.hide_item("Longitud_Label")
        dpg.hide_item("Longitud")

def update_progress(iteration, total, alfa, coherence):
    if total > 0:
        progress = (iteration / total) * 100
    else:
        progress = 0

    # Actualiza la barra de progreso y el texto
    dpg.set_value("progress_bar", progress / 100)
    dpg.set_value("progress_text", f"Progreso: {progress:.2f}% ({iteration}/{total})")

    # Cuando llegue a 100%, llamamos a stop_measurement
    if iteration >= total:
        stop_measurement(None, None, None)

def iniciar_medicion(data):
    global measurement_thread, stop_event
    stop_event = threading.Event()

    # Iniciar la medición en un hilo separado
    measurement_thread = threading.Thread(
        target=perform_measurement, 
        args=(data, update_progress, stop_event),
        daemon=True  # Para que el hilo se cierre al cerrar la aplicación
    )
    measurement_thread.start()

def start_measurement(sender, app_data, user_data):
    global is_measuring, measurement_data, measurement_thread, stop_event
    is_measuring = True

    # Recuperar los valores del formulario
    measurement_data["identification"] = dpg.get_value("Identificacion")
    measurement_data["localization"] = dpg.get_value("Localizacion")
    measurement_data["gps_enabled"] = dpg.get_value("GPS")
    measurement_data["latitude"] = dpg.get_value("Latitud") if measurement_data["gps_enabled"] else None
    measurement_data["longitude"] = dpg.get_value("Longitud") if measurement_data["gps_enabled"] else None
    measurement_data["averages"] = dpg.get_value("Promediaciones")
    measurement_data["sample_rate"] = int(dpg.get_value("Muestreo"))
    measurement_data["number_of_samples"] = int(dpg.get_value("Muestras"))

    # Iniciar la medición con los datos almacenados
    iniciar_medicion(measurement_data)

    # Ocultar la ventana de configuración
    dpg.hide_item("config_window")

    # Ajustar el viewport a pantalla completa
    dpg.configure_item("measurement_window", width=screen_width, height=screen_height, no_move=True, no_resize=True)
    dpg.set_viewport_width(screen_width)
    dpg.set_viewport_height(screen_height)
    dpg.set_viewport_pos((0, 0))

    # Mostrar la ventana de medición
    dpg.show_item("measurement_window")

def stop_measurement(sender, app_data, user_data):
    global is_measuring, stop_event

    if is_measuring and stop_event:
        stop_event.set()
        # Asegurarse de no hacer 'join' al mismo hilo, etc., según tu caso
        if measurement_thread and measurement_thread.is_alive():
            measurement_thread.join()
        is_measuring = False

    dpg.hide_item("measurement_window")

    # Restaurar el tamaño del viewport y mostrar configuración
    dpg.set_viewport_width(400)
    dpg.set_viewport_height(700)
    dpg.set_viewport_pos(((screen_width - 400) // 2, (screen_height - 700) // 2))
    dpg.show_item("config_window")

    # Mostrar la alerta
    dpg.configure_item("alert_window", show=True)

'''
    # Restaurar el tamaño del viewport y mostrar configuración
    dpg.set_viewport_width(400)
    dpg.set_viewport_height(700)
    dpg.set_viewport_pos(((screen_width - 400) // 2, (screen_height - 700) // 2))
    dpg.show_item("config_window")
'''

def exit_application(sender, app_data, user_data):
    # Si se está midiendo, detener la medición primero
    if is_measuring:
        stop_measurement(sender, app_data, user_data)
    dpg.stop_dearpygui()

# Crear el contexto
dpg.create_context()

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        #dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (150, 100, 100), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvInputInt):
        #dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (100, 150, 100), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

# Cargar fuente personalizada
with dpg.font_registry():
    try:
        default_font = dpg.add_font("Roboto-Regular.ttf", 20)  # Asegúrate de tener esta fuente en el mismo directorio
        dpg.bind_font(default_font)
    except:
        print("Error al cargar la fuente 'Roboto-Regular.ttf'. Asegúrate de que el archivo existe.")
        sys.exit(1)

# Crear la ventana de configuración
with dpg.window(label="Configuracion", tag="config_window", width=400, height=700, no_move=True, no_resize=True, no_title_bar=True):
    dpg.add_text("Configuracion", pos=(150, 40))
    dpg.add_spacer(height=10)

    # Contenedor para centrar automáticamente
    with dpg.group(horizontal=False, pos=(50, 80)):
        dpg.add_text("Identificacion")
        dpg.add_input_text(tag="Identificacion", default_value="Identificacion 1", width=300)
        dpg.add_text("Localizacion")
        dpg.add_input_text(tag="Localizacion", default_value="Localizacion 1", width=300)
        dpg.add_text("Activar GPS")
        dpg.add_checkbox(tag="GPS", callback=toggle_gps)

        dpg.add_text("Latitud", tag="Latitud_Label", show=False)
        dpg.add_input_float(tag="Latitud", default_value=0.0, width=300, show=False, format="%0.8f", step=0, step_fast=0)
        dpg.add_text("Longitud", tag="Longitud_Label", show=False)
        dpg.add_input_float(tag="Longitud", default_value=0.0, width=300, show=False, format="%0.8f", step=0, step_fast=0)

        dpg.add_text("Promediaciones")
        dpg.add_input_int(tag="Promediaciones", default_value=50, min_value=0, max_value=100, width=300)
        dpg.add_text("Muestreo")
        dpg.add_combo(tag="Muestreo", items=[32000, 44100, 48000], default_value=48000, width=300)
        dpg.add_text("Muestras")
        dpg.add_combo(tag="Muestras", items=[2048, 4096, 8192], default_value=4096, width=300)

    with dpg.group(horizontal=False, pos=(150, 600)):
        dpg.add_button(tag="Iniciar", label="Iniciar Medicion", callback=start_measurement)
        dpg.add_button(tag="Salir", label="Salir", callback=exit_application)

# Ventana modal (alert) que se muestra al detener la medición
with dpg.window(
    label="Archivos Guardados",
    tag="alert_window",
    modal=True,
    show=False,
    no_title_bar=True,
    width=ALERT_WIDTH,
    height=ALERT_HEIGHT,
    pos=(alert_pos_x, alert_pos_y),
    no_move=True
):
    dpg.add_text("¡Archivos guardados con éxito!\nEstán en la carpeta: C:/ruta/inventada")
    dpg.add_spacer(height=10)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Volver", callback=close_alert)
        dpg.add_button(label="Ir a la carpeta", callback=open_folder)
        
# Crear la ventana de medición
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
    # Título de la medición
    dpg.add_text("Medicion en Progreso", color=(255, 255, 255), tag="measurement_title")
    dpg.add_spacer(height=10)

    # Grupo vertical principal para organizar los elementos
    with dpg.group(horizontal=False):
        # Grupo para los recuadros de gráficos, centrados
        with dpg.group(horizontal=True, horizontal_spacing=50):
            # Primer recuadro: Coherencia
            with dpg.child_window(
                label="Coherencia",
                width=(screen_width / 2) - 150,
                height=screen_height - 300,
                border=False,
                tag="coherence_box"
            ):
                dpg.add_text("Coherencia", color=(255, 255, 255), tag="coherence_title")
                # Placeholder: dibujo de un rectángulo gris
                with dpg.drawlist(width=(screen_width / 2) - 150, height=screen_height - 300 - 30):
                    dpg.draw_rectangle(
                        pmin=(0, 0),
                        pmax=((screen_width / 2) - 150, screen_height - 300 - 30),
                        color=(200, 200, 200, 255),
                        fill=(100, 100, 100, 255),
                        thickness=1
                    )

            # Segundo recuadro: Absorción
            with dpg.child_window(
                label="Absorción",
                width=(screen_width / 2) - 150,
                height=screen_height - 300,
                border=False,
                tag="absorption_box"
            ):
                dpg.add_text("Absorción", color=(255, 255, 255), tag="absorption_title")
                # Placeholder: dibujo de un rectángulo gris
                with dpg.drawlist(width=(screen_width / 2) - 150, height=screen_height - 300 - 30):
                    dpg.draw_rectangle(
                        pmin=(0, 0),
                        pmax=((screen_width / 2) - 150, screen_height - 300 - 30),
                        color=(200, 200, 200, 255),
                        fill=(100, 100, 100, 255),
                        thickness=1
                    )

        # Spacer para separar los gráficos de la barra de progreso
        dpg.add_spacer(height=50)

        # Grupo horizontal para la barra de progreso y el texto de progreso
        with dpg.group(horizontal=True, horizontal_spacing=20):
            # Barra de progreso
            dpg.add_progress_bar(
                tag="progress_bar",
                default_value=0.0,
                width=screen_width - 300  # Ajusta el ancho según sea necesario
            )

            # Texto de progreso
            dpg.add_text("Progreso: 0.00% (0/0)", tag="progress_text", color=(255, 255, 255))

    # Botón para detener la medición, ubicado al fondo derecho
    dpg.add_spacer(height=30)  # Espacio antes del botón
    dpg.add_button(
        tag="Detener",
        label="Detener Medicion",
        callback=stop_measurement,
        width=150,
        pos=(screen_width - 200, screen_height - 100)  # Ajusta la posición si es necesario
    )


# Configurar el viewport
dpg.create_viewport(title='Formulario de Configuracion', width=400, height=700, resizable=False, decorated=False)
dpg.setup_dearpygui()

dpg.set_viewport_pos((viewport_x, viewport_y))
dpg.show_viewport()

# Iniciar Dear PyGui
dpg.start_dearpygui()
dpg.destroy_context()
