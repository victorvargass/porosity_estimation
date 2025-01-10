import dearpygui.dearpygui as dpg

def create_alert_window(open_folder, close_alert, green_button_theme, dark_yellow_button_theme):
    with dpg.window(
        label="Archivos guardados",
        tag="alert_window",
        modal=True,
        show=False,
        no_title_bar=True,
        width=250,
        height=130,  # Ajustamos un poco la altura para mejor diseño
        pos=(100, 300),
        no_move=True
    ):
        # Crear un grupo para centrar vertical y horizontalmente
        dpg.add_spacer(height=10)  # Más espacio entre el texto y los botones
        with dpg.group(horizontal=False):  # Ajustamos la indentación
            dpg.add_text("", tag="alert_text", indent=20)  # Ajustamos el texto un poco más a la izquierda
            dpg.add_spacer(height=5)  # Más espacio entre el texto y los botones
            
            # Botón "Ver resultados"
            dpg.add_button(
                label="Ver resultados", 
                tag="open_folder_button", 
                callback=open_folder, 
                user_data="",
                indent=65
            )
            dpg.bind_item_theme("open_folder_button", green_button_theme)

            # Botón "Volver"
            dpg.add_button(
                label="Volver", 
                tag="back", 
                callback=close_alert,
                indent=90
            )
            dpg.bind_item_theme("back", dark_yellow_button_theme)