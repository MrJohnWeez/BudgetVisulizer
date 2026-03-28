from pathlib import Path
import webbrowser

from plotly.graph_objs import Figure
from dash import Dash, dcc, html
from data_loader import DataLoader

WORKBOOK_NAME = "Assets/Budget.xlsx"
REDACT_VALUES = True


def run_app() -> None:
    data_loader = DataLoader(Path(WORKBOOK_NAME), REDACT_VALUES)
    app = Dash(__name__)
    app.layout = html.Div(
        [
            _create_plot_section("Custom Plots", data_loader.get_line_plots()),
            _create_plot_section("Vender Plots", data_loader.get_vender_plots()),
            _create_plot_section(
                "Yearly Vender Summary", data_loader.get_vender_pie_charts()
            ),
            _create_plot_section(
                "Yearly Category Summary", data_loader.get_category_pie_charts()
            ),
            _create_plot_section(
                "Yearly Payment Summary", data_loader.get_payment_type_pie_charts()
            ),
            _create_plot_section(
                "Yearly Project Summary", data_loader.get_project_pie_charts()
            ),
        ],
        className="scroll-container",
    )
    app.run(debug=True)


def _create_plot_section(title: str, plots: list[Figure]) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="title-bar"),
            html.Div(
                [dcc.Graph(figure=fig, className="graph") for fig in plots],
                className="grid-container",
            ),
        ],
        className="section",
    )


def open_browser():
    webbrowser.open("http://127.0.0.1:8050/")


if __name__ == "__main__":
    # Timer(1, open_browser).start()
    run_app()
