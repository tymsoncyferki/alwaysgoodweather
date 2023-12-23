from shiny import App, render, ui, reactive
from joblib import load
from data.data import plot_map
from weather_api import WeatherApi
import numpy as np
import shinyswatch

model = load('temp_model.joblib')

app_ui = ui.page_fluid(

    shinyswatch.theme.minty(),

    ui.row(
        ui.column(3),
        ui.column(6,
                  ui.tags.br(),
                  ui.panel_title("alwaysgoodweather.com"),
                  ui.navset_tab(
                      ui.nav("Weather",
                             # ui.input_selectize("prompt", "Enter location", choices=[]),
                             ui.tags.br(),
                             ui.tags.form(
                                 ui.input_text("location", label="", placeholder="Enter location"),
                                 ui.input_action_button("go", label="go")
                             ),
                             ui.output_text("autocomplete"),
                             ui.tags.br(),
                             # ui.output_text_verbatim("current_temp"),
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
    # @reactive.Effect()
    # def _():
    #     prompt = input.location()
    #     response, code = WeatherApi.get_locations(prompt)
    #     print(session)
    #     if code == 200:
    #         names = [city['name'] for city in response]
    #         ui.update_selectize(
    #             id="prompt",
    #             choices=names,
    #             server=True
    #         )

    @render.text
    def autocomplete():
        prompt = input.location()
        response, code = WeatherApi.get_locations(prompt)
        names = ""
        n = len(response)
        if code == 200:
            for i, city in enumerate(response):
                if i == 3:
                    break
                if i + 1 == n:
                    names += f"{city['name']}, {city['country']}"
                else:
                    names += f"{city['name']}, {city['country']}\n "

        return names

    def get_data():
        location = input.location()
        response, code = WeatherApi.get_response_weather(location)
        return response, code

    def scale_temp(lat, lon, temp):
        predictions = model.predict(np.array([[lat, lon]]))[0]

        if temp < predictions[2]:
            slope, intercept = np.polyfit([predictions[0], predictions[2]], [predictions[3], predictions[5]], deg=1)
        else:
            slope, intercept = np.polyfit([predictions[1], predictions[2]], [predictions[4], predictions[5]], deg=1)

        return slope * temp + intercept

    # @render.text
    # def current_temp():
    #     response, code = get_data()
    #     print(response)
    #     try:
    #         region = response['location']['region']
    #         if region != "":
    #             region = f'{region}, '
    #         return f"Current weather in {response['location']['name']}, {region}" \
    #                f"{response['location']['country']} is {response['current']['temp_c']} Celsius degrees"
    #     except KeyError:
    #         return ""

    @output
    @render.text
    async def desired_temp():
        input.go()

        with reactive.isolate():

            response, code = get_data()

            try:
                lat = response['location']['lat']
                lon = response['location']['lon']

                temp = scale_temp(lat, lon, response['current']['temp_c'])

                return f"Yeeeey! The temperature is {round(temp)} Celsius degrees. Have fun"
            except (KeyError, IndexError):
                return "No data"

    @render.plot
    def world_map():
        # return plot_map(input.number(), 2, model, -input.number() + 550)
        return plot_map(475, 2, model, 75)


app = App(app_ui, server)
