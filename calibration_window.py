import dearpygui.dearpygui as dpg
from utils import calibration_factor, perform_calibration
import pandas as pd

# Variables globales para almacenar los datos adquiridos
h12_I = None
h12_II = None
freqs = None

fs = 48000 # Sample rate
N = 2048 # 2048 4096 8192 # Number of samples
M = 50 # Number of iterations

# Función para cargar imágenes y registrar texturas
def load_image(file_path):
    width, height, channels, data = dpg.load_image(file_path)
    with dpg.texture_registry():
        texture_id = dpg.add_static_texture(width, height, data)
    return texture_id

# Función para crear la ventana y el stepper
def create_stepper_window(viewport_width, viewport_height, exit_application, green_button_theme, blue_button_theme, red_button_theme, viewport_x, viewport_y):
    global current_step

    current_step = 0

    # Cargar texturas para las imágenes
    step1_texture_id = load_image("src/calibration_I.png")  # Cambia a la ruta de tu imagen
    step2_texture_id = load_image("src/calibration_II.png")  # Cambia a la ruta de tu imagen

    # Lista de contenidos para cada paso
    step_contents = [
        "Conectar micrófonos en posición inicial.",
        "Conectar micrófonos en posición intercambiada.",
        "Exportar archivo de calibración."
    ]

    # Función para avanzar al siguiente paso
    def next_step(sender, app_data):
        global current_step
        if current_step < 2:
            current_step += 1
            update_step()

    # Función para adquirir datos del paso actual
    def acquire_data():
        global h12_I, h12_II, current_step, freqs
        if current_step == 0:
            dpg.configure_item("next_button", show=False)
            dpg.set_value("action_status", "")
            h12_I, freqs = perform_calibration(fs, N, M)
            if h12_I is not None:
                dpg.set_value("action_status", "H12 (I) adquirido con éxito.")
                dpg.configure_item("next_button", show=True)
                dpg.configure_item("acquire_button", label="Repetir obtención H12 (I)")

        elif current_step == 1:
            dpg.configure_item("next_button", show=False)
            dpg.set_value("action_status", "")
            h12_II, freqs = perform_calibration(fs, N, M)
            if h12_II is not None:
                dpg.set_value("action_status", "H12 (II) adquirido con éxito.")
                dpg.configure_item("next_button", show=True)
                dpg.configure_item("acquire_button", label="Repetir obtención H12 (II)")

    # Función para exportar archivo
    def export_file(sender, app_data, user_data):
        N = user_data
        dpg.configure_item("action_status", pos=(500 // 2 - 100, 70))
        if h12_I is not None and h12_I.size > 0 and h12_II is not None and h12_II.size > 0:
            hc = calibration_factor(h12_I, h12_II, freqs)
            hc_df = pd.DataFrame(hc)
            hc_df.to_csv(f"results/hc_calibration_{N}.csv", index=False)
            # Aquí puedes implementar tu lógica para exportar el archivo con los datos de h12_I y h12_II
            dpg.set_value("action_status", "Archivo exportado con éxito")
        else:
            dpg.set_value("action_status", "No se pueden exportar datos incompletos")

    # Función para actualizar el contenido del paso mostrado
    def update_step():
        dpg.set_value("content_text", step_contents[current_step])
        
        dpg.configure_item("next_button", show=False)

        # Mostrar/ocultar controles según el paso
        dpg.configure_item("image_step1", show=current_step == 0)
        dpg.configure_item("image_step2", show=current_step == 1)
        dpg.configure_item("export_button", show=current_step == 2)
        if current_step == 1:
            dpg.configure_item("acquire_button", label="Obtener H12 (II)")
            dpg.set_value("action_status", "")
        if current_step == 2:
            dpg.set_viewport_pos([viewport_x, viewport_y + 200])  # Cambia los valores de [0, 200] según sea necesario
            dpg.set_viewport_height(150)
            dpg.configure_item("export_button", pos=(10, 50))
            dpg.configure_item("Salir", pos=(10, 100))

            dpg.set_value("action_status", "")
        dpg.configure_item("acquire_button", show=current_step in [0, 1])

    # Crear la ventana con el stepper
    with dpg.window(
        label="Stepper", 
        width=viewport_width, 
        height=viewport_height,
        no_move=True, 
        no_resize=True,
        no_title_bar=True
    ):
        # Texto para mostrar contenido dinámico
        dpg.add_text(step_contents[0], tag="content_text")

        dpg.add_spacer(height=20)  # Más espacio entre el texto y los botones
        # Imagen para paso 1
        dpg.add_image(tag="image_step1", texture_tag=step1_texture_id, width=480, height=270, show=True)

        # Imagen para paso 2
        dpg.add_image(tag="image_step2", texture_tag=step2_texture_id, width=480, height=270, show=False)

        dpg.add_spacer(height=20)  # Más espacio entre el texto y los botones
        # Botón para adquirir datos (visible en pasos 0 y 1)
        dpg.add_button(label="Obtener H12 (I)", tag="acquire_button", callback=acquire_data, width=480, show=True)
        dpg.bind_item_theme("acquire_button", blue_button_theme)

        # Botón para exportar datos (visible en paso 2)
        dpg.add_button(label="Exportar archivo Hc", tag="export_button", callback=export_file, user_data=N, width=480, show=False)
        dpg.bind_item_theme("export_button", blue_button_theme)

        # Botones para navegación entre pasos
        dpg.add_button(label="Siguiente", tag="next_button", callback=next_step, width=480, show=False)
        dpg.bind_item_theme("next_button", green_button_theme)

        dpg.add_spacer(height=20)  # Más espacio entre el texto y los botones
        # Mensaje de estado
        dpg.add_text("", tag="action_status", color=(0, 255, 0), pos=(500 // 2 - 100, 440))

        
        dpg.add_spacer(height=60)  # Más espacio entre el texto y los botones
        # Botón "Salir" con tema rojo
        dpg.add_button(tag="Salir", label="Salir", callback=exit_application, width=480)
        dpg.bind_item_theme("Salir", red_button_theme)
        


    # Llamamos a la función para crear la ventana
    dpg.create_context()

# Exportar la función para usarla en otro archivo
