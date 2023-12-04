from shiny import App, render, ui
from joblib import load
from data.data import plot_map

app_ui = ui.page_fluid(
    ui.panel_title("alwaysgoodweather.com"),
    ui.input_slider("number", "Degrees", 0, 500, 100),
    ui.output_text_verbatim("txt"),
    ui.output_plot("plot")
)


def server(input, output, session):
    @render.text
    def txt():
        return f"weather is fucked {input.number() * 2} degrees"

    @render.plot
    def plot():
        model = load('temp_model.joblib')
        return plot_map(input.number(), 2, model, -input.number() + 550)


app = App(app_ui, server)
