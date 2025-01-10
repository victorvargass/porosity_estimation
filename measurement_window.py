import dearpygui.dearpygui as dpg

def create_measurement_window(screen_width, screen_height, orange_line_theme, blue_line_theme, red_button_theme, stop_measurement):
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
                    label="Detener medición",
                    callback=stop_measurement,
                    width=150,
                    pos=(screen_width - 200, screen_height - 100))
        dpg.bind_item_theme("Detener", red_button_theme)