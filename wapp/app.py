from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.panel_title("alwaysgoodweather.com"),
    ui.input_slider("number", "Degrees", 0, 100, 20),
    ui.output_text_verbatim("txt"),
)


def server(input, output, session):

    @render.text
    def txt():
        return f"waether is fucked {input.number() * 2} degrees"


app = App(app_ui, server)
