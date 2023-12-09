from shiny import App, render, ui
from joblib import load
from data.data import plot_map
from weather_api import WeatherApi
import numpy as np

app_ui = ui.page_fluid(
    ui.row(
        ui.column(3),
        ui.column(6,
                  ui.panel_title("alwaysgoodweather.com"),
                  ui.navset_tab(
                      ui.nav("Weather",
                             ui.input_text("location", "Enter location:"),
                             ui.output_text_verbatim("current_temp"),
                             ui.output_text_verbatim("desired_temp"),
                             ),
                      ui.nav("About",
                             # ui.input_slider("number", "Degrees", 100, 500, 150),
                             ui.output_plot("world_map"),
                             ),
                  ),
                  ),
        ui.column(3)
    ),

)


def server(input, output, session):

    def get_data():
        location = input.location()
        response, code = WeatherApi.get_response_weather(location)
        return response, code

    @render.text
    def current_temp():
        response, code = get_data()
        print(response)
        try:
            region = response['location']['region']
            if region != "":
                region = f'{region}, '
            return f"Current weather in {response['location']['name']}, {region}" \
                   f"{response['location']['country']} is {response['current']['temp_c']} Celsius degrees"
        except KeyError:
            return ""

    @render.text
    def desired_temp():
        response, code = get_data()
        model = load('temp_model.joblib')
        try:
            lat = response['location']['lat']
            lon = response['location']['lon']
            temps = model.predict(np.array([[lat, lon]]))
            return f"Yeeeey! The temperature is {round(temps[0][5], 2)} Celsius degrees. Have fun"
        except (KeyError, IndexError):
            return ""

    @render.plot
    def world_map():
        model = load('temp_model.joblib')
        # return plot_map(input.number(), 2, model, -input.number() + 550)
        return plot_map(475, 2, model, 75)


app = App(app_ui, server)
