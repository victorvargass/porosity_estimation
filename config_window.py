# -----------------------------
#  VENTANA DE CONFIGURACIÓN
# -----------------------------
import dearpygui.dearpygui as dpg

def create_config_window(font_large, window_width, window_height, green_button_theme, red_button_theme, start_measurement, exit_application, toggle_gps):

    with dpg.window(
        label="Configuración inicial",
        tag="config_window",
        width=window_width, height=window_height,
        no_move=True, no_resize=True, no_title_bar=True
    ):
        dpg.add_text("Configuración inicial", pos=(125, 40), tag="config_text")
        dpg.bind_item_font("config_text", font_large)  # Asigna la fuente al texto
        
        with dpg.group(horizontal=False, pos=(50, 90)):
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
                        default_value=200,
                        min_value=0,
                        max_value=1000,
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

            dpg.add_spacer(height=20)

            dpg.add_text("Humedad")
            dpg.add_input_float(
                tag="humidity_percentage",
                default_value=0.0,
                width=150,
                step=0,
                format="%.2f"
            )
            dpg.add_spacer(height=20)

            dpg.add_text("¿Calibración Hc?")
            dpg.add_checkbox(tag="hc_calibration", callback=toggle_hc_calibration)

            # Input de archivo para Calibración HC
            with dpg.group(horizontal=False, tag="hc_file", show=False):
                dpg.add_button(label="Seleccionar archivo de calibración", callback=select_file_with_native_dialog)
                dpg.add_text("No se ha seleccionado ningún archivo.", tag="selected_file_text")
                dpg.add_input_text(tag="hc_file_path", default_value="", show=False)

            # Botón "Iniciar" con tema verde
            dpg.add_button(tag="Iniciar", label="Iniciar medición", callback=start_measurement, width=310)
            dpg.bind_item_theme("Iniciar", green_button_theme)

            dpg.add_spacer(height=20)

            # Botón "Salir" con tema rojo
            dpg.add_button(tag="Salir", label="Salir", callback=exit_application, width=310)
            dpg.bind_item_theme("Salir", red_button_theme)
