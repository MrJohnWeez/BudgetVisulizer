from pathlib import Path
from threading import Timer
import webbrowser

from dash import Dash, dcc, html
from data_loader import DataLoader

WORKBOOK_NAME = "Assets/Budget.xlsx"


def run_app() -> None:
    data_loader = DataLoader(Path(WORKBOOK_NAME))
    app = Dash(__name__)
    plots = data_loader.get_plots()
    app.layout = html.Div(
        [
            html.Div(
                [dcc.Graph(figure=fig, className="graph") for fig in plots],
                className="grid-container",
            )
        ]
    )
    app.run(debug=True)


def open_browser():
    webbrowser.open("http://127.0.0.1:8050/")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    run_app()
