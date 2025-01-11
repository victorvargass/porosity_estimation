# styles.py
from dearpygui import dearpygui as dpg
import sys

def load_styles_and_fonts():
    # Crear el contexto de estilos y temas
    dpg.create_context()

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

    with dpg.theme() as green_button_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [102, 187, 106])  # Verde suave
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [76, 175, 80])  # Verde más intenso al pasar el mouse
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [67, 160, 71])  # Verde oscuro al presionar

    with dpg.theme() as red_button_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [244, 67, 54])  # Rojo suave
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [229, 57, 53])  # Rojo más intenso al pasar el mouse
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [211, 47, 47])  # Rojo oscuro al presionar

    with dpg.theme() as dark_yellow_button_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 214, 10])  # Amarillo oscuro
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [255, 193, 7])  # Más oscuro al pasar el mouse
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [255, 179, 0])  # Aún más oscuro al presionar

    with dpg.theme() as blue_button_theme:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, [33, 150, 243])  # Azul claro
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [30, 136, 229])  # Azul más intenso al pasar el mouse
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [25, 118, 210])  # Azul aún más oscuro al presionar

    # Registrar y cargar fuentes
    with dpg.font_registry():
        try:
            default_font = dpg.add_font("src/Roboto-Regular.ttf", 16)
            font_large = dpg.add_font("src/Roboto-Regular.ttf", 20)
            dpg.bind_font(default_font)
        except:
            print("Error al cargar la fuente 'src/Roboto-Regular.ttf'. Asegúrate de que el archivo existe.")
            sys.exit(1)
    
    # Retornar estilos, temas y fuentes
    return {
        "orange_line_theme": orange_line_theme,
        "blue_line_theme": blue_line_theme,
        "green_button_theme": green_button_theme,
        "red_button_theme": red_button_theme,
        "dark_yellow_button_theme": dark_yellow_button_theme,
        "blue_button_theme": blue_button_theme,
        "default_font": default_font,
        "font_large": font_large,
    }