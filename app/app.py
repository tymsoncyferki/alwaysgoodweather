import random

from shiny import App, render, ui, reactive
from joblib import load
from weather_api import WeatherApi
import numpy as np
import shinyswatch
from datetime import datetime, timedelta
from plotnine import ggplot, geom_line, geom_point, geom_area, geom_ribbon, aes, theme, scale_y_continuous,\
    scale_x_continuous, element_rect, scale_x_datetime, stat_smooth, theme_minimal, element_blank
from mizani.formatters import date_format
from mizani.breaks import date_breaks

model = load('temp_model.joblib')

response_l = dict()
code_l = dict()
response_w = dict()
code_w = dict()

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
                          ui.output_ui("forecast"),
                      ),
                  ),
                  ),
        ui.column(3)
    ),
)


def server(input, output, session):

    @reactive.Effect()
    def _():
        """
        Gets locations based on current prompt
        """
        prompt = input.location()
        global response_l, code_l
        response_l, code_l = WeatherApi.get_locations(prompt)

    @reactive.Effect()
    def _():
        """
        Gets forecast in provided location
        """
        input.go()
        with reactive.isolate():
            location = input.location()
            global response_w, code_w
            response_w, code_w = WeatherApi.get_response_forecast(location, 2)

    @render.text
    def loc1():
        """ Main location name. Displayed at all times """
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
        """ Second location recommendation. Available only on reload """
        input.location()
        global response_l, code_l
        name = ""
        if code_l == 200:
            for i, city in enumerate(response_l):
                if i == 1:
                    name += f"{city['name']}, {city['country']}"
                    break
        if input.go():
            return ""
        return name

    @render.text
    def loc3():
        """ Third location recommendation. Available only on reload """
        input.location()
        global response_l, code_l
        name = ""
        if code_l == 200:
            for i, city in enumerate(response_l):
                if i == 2:
                    name += f"{city['name']}, {city['country']}"
                    break
        if input.go():
            return ""
        return name

    @render.ui
    def forecast():
        """
        Displays main forecast UI after clicking GO button
        """
        input.go()

        global response_w, code_w

        if code_w == 200:
            local_time = response_w['location']['localtime']
            local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

            return ui.div(
                ui.row(
                    ui.div({"class": "col-auto"},
                           ui.output_ui("icon")
                           ),
                    ui.div({"class": "col-auto"},
                           ui.h1(ui.output_text("temp"), style="font-size: 3em;")),
                    ui.div({"class": "col-auto"},
                           ui.span(ui.output_text("time")),
                           ui.span(ui.output_text("wind")),
                           ui.span(ui.output_text("rain")))
                ),
                ui.div(ui.output_plot("plot", height=100), style="margin-left: -6%"),
                ui.tags.style(".irs-grid-pol.small {height: 0px;}", type="text/css"),
                ui.input_slider("time", label="", min=local_date,
                                max=(local_date + timedelta(hours=24)), step=timedelta(hours=1),
                                value=local_date, time_format="%H", post=":00", width='95%')

            )

    @render.ui
    def icon():
        """
        Displays weather icon
        """
        time = input.time() + timedelta(hours=1)
        hour = time.hour

        global response_w

        code = response_w['forecast']['forecastday'][0]['hour'][hour]["condition"]['code']

        if response_w['forecast']['forecastday'][0]['hour'][hour]['is_day'] == 1:
            if code == 1000 or code == 1003:
                return ui.img(src="https://cdn.weatherapi.com/weather/64x64/day/113.png", height='100%',
                              style="display: inline-block;")
            else:
                return ui.img(src="https://cdn.weatherapi.com/weather/64x64/day/116.png", height='100%',
                              style="display: inline-block;")
        else:
            return ui.img(src="https://cdn.weatherapi.com/weather/64x64/night/116.png", height='100%',
                          style="display: inline-block;")

    @render.text
    def temp():
        """ Returns desired temperature """
        time = input.time() + timedelta(hours=1)
        hour = time.hour

        global response_w

        lat = response_w['location']['lat']
        lon = response_w['location']['lon']

        local_time = response_w['location']['localtime']
        local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

        if time.date() <= local_date.date():
            temperature = response_w['forecast']['forecastday'][0]['hour'][hour]['temp_c']
        else:
            temperature = response_w['forecast']['forecastday'][1]['hour'][hour]['temp_c']

        temp_scaled = round(scale_temp(lat, lon, temperature))

        return f"{temp_scaled}°"

    @render.text
    def wind():
        """ Returns desired wind speed """
        time = input.time() + timedelta(hours=1)
        hour = time.hour

        global response_w

        local_time = response_w['location']['localtime']
        local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

        if time.date() <= local_date.date():
            wind_kph = response_w['forecast']['forecastday'][0]['hour'][hour]['wind_kph']
        else:
            wind_kph = response_w['forecast']['forecastday'][1]['hour'][hour]['wind_kph']

        wind_scaled = round(wind_kph / 5) + 1

        return f"Wind: {wind_scaled}kph"

    @render.text
    def rain():
        """ Returns desired precipitation """
        time = input.time() + timedelta(hours=1)
        hour = time.hour

        global response_w

        local_time = response_w['location']['localtime']
        local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

        if time.date() <= local_date.date():
            rain_chance = response_w['forecast']['forecastday'][0]['hour'][hour]['chance_of_rain']
        else:
            rain_chance = response_w['forecast']['forecastday'][1]['hour'][hour]['chance_of_rain']

        print(rain_chance)
        rain_scaled = round(rain_chance / 10)

        if rain_scaled == 0:
            rain_scaled = rain_scaled + random.randint(0, 3)
        else:
            rain_scaled = rain_scaled - random.randint(0, 3)

        return f"Rain: {rain_scaled}%"

    @render.text
    def time():
        time = input.time() + timedelta(hours=1)
        hour = time.hour

        local_time = response_w['location']['localtime']
        local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')

        if time.date() <= local_date.date():
            time_response = response_w['forecast']['forecastday'][0]['hour'][hour]['time']
        else:
            time_response = response_w['forecast']['forecastday'][1]['hour'][hour]['time']

        return f"{time_response}"

    @render.plot
    def plot():

        input.go()

        global response_w

        local_time = response_w['location']['localtime']
        local_date = datetime.strptime(local_time, '%Y-%m-%d %H:%M')
        x = [local_date]
        for i in range(24):
            x.append(x[i] + timedelta(hours=1))

        temps = []
        for date in x:
            if date.date() <= local_date.date():
                temps.append(response_w['forecast']['forecastday'][0]['hour'][date.hour]['temp_c'])
            else:
                temps.append(response_w['forecast']['forecastday'][1]['hour'][date.hour]['temp_c'])

        lat = response_w['location']['lat']
        lon = response_w['location']['lon']

        y = [round(scale_temp(lat, lon, temperature)) for temperature in temps]
        labels = [str(date.hour % 24) for date in x]
        x = list(range(25))

        temp_plot = (
                ggplot(aes(x, y)) +
                geom_line() +
                geom_ribbon(aes(ymax='y', ymin=min(y)-1), fill='lightblue', alpha=0.3) +
                scale_y_continuous(limits=(min(y) - 1, max(y) + 1)) +
                scale_x_continuous(breaks=x[::2], labels=labels[::2]) +
                theme(figure_size=(16, 4), rect=element_rect(alpha=0),
                      panel_grid_major=element_blank(),
                      panel_grid_minor=element_blank(),
                      panel_border=element_blank(),
                      axis_line=element_blank(),
                      axis_text_y=element_blank(),
                      axis_ticks=element_blank(),
                      panel_spacing_y=0
                      )
        )
        return temp_plot

    def scale_temp(lat, lon, temp):
        """ Scales temperature to desired value """
        predictions = model.predict(np.array([[lat, lon]]))[0]

        if temp < predictions[2]:
            coefficients = np.polyfit([predictions[0], predictions[2]], [predictions[3], predictions[5]], deg=1)
        else:
            coefficients = np.polyfit([predictions[1], predictions[2]], [predictions[4], predictions[5]], deg=1)

        slope = coefficients[0]
        intercept = coefficients[1]

        return slope * temp + intercept


app = App(app_ui, server)
