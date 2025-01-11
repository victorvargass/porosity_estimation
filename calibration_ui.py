from dearpygui import dearpygui as dpg
import screeninfo
import queue

# -----------------------------
#  VARIABLES / ESTADO GLOBAL
# -----------------------------
# Variables globales para almacenar los datos adquiridos
h12_I = None
h12_II = None

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

viewport_width = 500
viewport_height = 550

viewport_x = (screen_width - viewport_width) // 2
viewport_y = (screen_height - viewport_height) // 2

def exit_application(sender, app_data, user_data):
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
from calibration_window import create_stepper_window

create_stepper_window(viewport_width, viewport_height, exit_application, green_button_theme, blue_button_theme, red_button_theme, viewport_x, viewport_y)

# -----------------------------
#  CREAR VIEWPORT & ARRANCAR (BUCLE MANUAL)
# -----------------------------
dpg.create_viewport(title="Calibracion Hc", width=viewport_width, height=viewport_height, resizable=False, decorated=False)
dpg.setup_dearpygui()
dpg.set_viewport_pos((viewport_x, viewport_y))
dpg.show_viewport()

# En lugar de dpg.start_dearpygui(), hacemos un bucle manual:
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()
