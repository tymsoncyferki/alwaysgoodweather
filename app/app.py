from shiny import App, render, ui, reactive
from joblib import load
from data.data import plot_map
from weather_api import WeatherApi
import numpy as np
import shinyswatch
from PIL import Image
import requests
from io import BytesIO
from shiny.types import ImgData

model = load('temp_model.joblib')

response_l = None
code_l = None
response_w = None
code_w = None

app_ui = ui.page_fluid(

    shinyswatch.theme.minty(),
    ui.include_css("www/custom.css"),

    ui.row(
        ui.column(3),
        ui.column(6,
                  ui.tags.br(),
                  ui.panel_title("alwaysgoodweather.com"),
                  ui.navset_tab(
                      ui.nav(
                          "Forecast",
                             ui.tags.br(),

                             # input
                             ui.row(
                                 ui.div({"class": "col-9"},
                                        ui.input_text("location", label="", placeholder="Enter location",
                                                      width='100%')
                                        ),
                                 ui.div({"class": "col-3"},
                                        ui.input_action_button("go", label="Go", width='100%', class_="btn-primary")
                                        ),
                             ),

                             # suggestions
                             ui.output_text("loc1"),
                             ui.output_text("loc2"),
                             ui.output_text("loc3"),
                             ui.tags.br(),

                             # weather now
                             ui.output_ui("test"),

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

    shinyswatch.theme_picker_server()

    @reactive.Effect()
    def _():
        prompt = input.location()
        global response_l, code_l
        response_l, code_l = WeatherApi.get_locations(prompt)

    @reactive.Effect()
    def _():
        input.go()
        with reactive.isolate():
            location = input.location()
            global response_w, code_w
            response_w, code_w = WeatherApi.get_response_weather(location)

    @render.text
    def loc1():
        input.location()
        global response_l, code_l
        name = ""
        if code_l == 200:
            for i, city in enumerate(response_l):
                name += f"{city['name']}, {city['country']}"
                break
        return name

    @render.text
    def loc2():
        input.location()
        global response_l, code_l
        name = ""
        if code_l == 200:
            for i, city in enumerate(response_l):
                if i == 1:
                    name += f"{city['name']}, {city['country']}"
                    break
        return name

    @render.text
    def loc3():
        input.location()
        global response_l, code_l
        name = ""
        if code_l == 200:
            for i, city in enumerate(response_l):
                if i == 2:
                    name += f"{city['name']}, {city['country']}"
                    break
        return name

    # @render.text
    # def autocomplete():
    #     prompt = input.location()
    #     response, code = WeatherApi.get_locations(prompt)
    #     names = ""
    #     n = len(response)
    #     if code == 200:
    #         for i, city in enumerate(response):
    #             if i == 3:
    #                 break
    #             if i + 1 == n:
    #                 names += f"{city['name']}, {city['country']}"
    #             else:
    #                 names += f"{city['name']}, {city['country']}\n "
    #
    #     return names

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

    @render.image
    def image_now():
        input.go()

        with reactive.isolate():
            global response_w, code_w

            if code_w == 200:
                src = "www/night.png"

                return {"src": src}

    @render.ui
    def test():
        input.go()

        global response_w, code_w

        if code_w == 200:

            # calculate temp
            lat = response_w['location']['lat']
            lon = response_w['location']['lon']
            temp = round(scale_temp(lat, lon, response_w['current']['temp_c']))

            return ui.row(
                ui.div({"class": "col-auto"},
                       ui.img(src="https://cdn.weatherapi.com/weather/64x64/night/116.png", height='100%',
                              style="display: inline-block;")),
                ui.div({"class": "col-auto"},
                       ui.h1(f"{temp}°")),
                ui.div({"class": "col-auto"},
                       ui.span("Wind: 5m/s"),
                       ui.br(),
                       ui.span("Rain: 0%"))
            )

    @output
    @render.text
    async def desired_temp():
        input.go()

        with reactive.isolate():

            global response_w, code_w

            try:
                lat = response_w['location']['lat']
                lon = response_w['location']['lon']

                temp = scale_temp(lat, lon, response_w['current']['temp_c'])

                return f"Yeeeey! The temperature is {round(temp)} Celsius degrees. Have fun"
            except (KeyError, IndexError):
                return "No data"

    @render.plot
    def world_map():
        # return plot_map(input.number(), 2, model, -input.number() + 550)
        return plot_map(475, 2, model, 75)


app = App(app_ui, server)
