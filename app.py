from pathlib import Path
from threading import Timer
import webbrowser

from dash import Dash, dcc, html
from data_loader import DataLoader

WORKBOOK_NAME = "Assets/Budget.xlsx"


def run_app() -> None:
    data_loader = DataLoader(Path(WORKBOOK_NAME))
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div("Vender Plots", className="title-bar"),
                    html.Div(
                        [
                            dcc.Graph(figure=fig, className="graph")
                            for fig in data_loader.get_vender_plots()
                        ],
                        className="grid-container",
                    ),
                ],
                className="section",
            ),
            html.Div(
                [
                    html.Div("Yearly Pie Charts", className="title-bar"),
                    html.Div(
                        [
                            dcc.Graph(figure=fig, className="graph")
                            for fig in data_loader.get_yearly_pie_charts()
                        ],
                        className="grid-container",
                    ),
                ],
                className="section",
            ),
        ],
        className="scroll-container",
    )
    app.run(debug=True)


def open_browser():
    webbrowser.open("http://127.0.0.1:8050/")


if __name__ == "__main__":
    # Timer(1, open_browser).start()
    run_app()
