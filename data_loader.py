from pathlib import Path

from pandas import DataFrame, concat
from plotly.graph_objs import Figure
from plotly.express import line, bar, pie
import pandas as pd

from spreadsheet_items import (
    MONTHS,
    Category,
    Column,
    PaymentType,
    Project,
    Vender,
    get_options,
)


class DataLoader:
    def __init__(self, workbook_path: Path, redact_values: bool = False) -> None:
        self.df = _load_dataframe(workbook_path)
        self.redact_values = redact_values

    def get_line_plots(self) -> list[Figure]:
        return [
            _sum_line_graph(
                self.df,
                Column.CATEGORY,
                [
                    Category.GAS,
                    Category.ELECTRIC,
                    Category.WATER_SEWAGE,
                    Category.TRASH,
                    Category.INTERNET,
                ],
                "Utility Cost",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.CATEGORY,
                [Category.HOUSE_IMPROVEMENT, Category.TOOLS, Category.APPLIANCES],
                "House Spending",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.CATEGORY,
                [Category.FOOD, Category.TAKEOUT],
                "Food Costs",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.CATEGORY,
                [Category.CAR_GAS, Category.TRAILER],
                "Car & Trailer Costs",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.VENDER,
                [
                    Vender.HOME_DEPOT,
                    Vender.AMAZON,
                    Vender.KROGER,
                    Vender.LOWES,
                    Vender.MENARDS,
                    Vender.WALMART,
                    Vender.SAMS,
                    Vender.COSTCO,
                    Vender.GAME_STORES,
                    Vender.KOHLS,
                    Vender.HARBOR_FREIGHT_TOOLS,
                ],
                "Stores",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.VENDER,
                [
                    Vender.SPOTIFY,
                    Vender.PEACOCK_TV,
                    Vender.US_MOBILE,
                    Vender.NET10,
                    Vender.NETFLIX,
                    Vender.DISNEY_PLUS,
                ],
                "Subscriptions",
                self.redact_values,
            ),
            _sum_line_graph(
                self.df,
                Column.PROJECT,
                [p for p in Project],
                "House Projects",
                self.redact_values,
            ),
        ]

    def get_vender_plots(self) -> list[Figure]:
        return [
            _sum_bargraph(self.df, Column.VENDER, Vender.FAST_FOOD, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.ALTAFIBER, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.AMAZON, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.BANK, self.redact_values),
            _sum_bargraph(
                self.df, Column.VENDER, Vender.DUKE_ENERGY, self.redact_values
            ),
            _sum_bargraph(self.df, Column.VENDER, Vender.GCWW, self.redact_values),
            _sum_bargraph(
                self.df, Column.VENDER, Vender.HOME_DEPOT, self.redact_values
            ),
            _sum_bargraph(self.df, Column.VENDER, Vender.KROGER, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.LOWES, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.MENARDS, self.redact_values),
            _sum_bargraph(self.df, Column.VENDER, Vender.SAMS, self.redact_values),
        ]

    def get_vender_pie_charts(self) -> list[Figure]:
        return _yearly_pie_charts(self.df, Column.VENDER, self.redact_values)

    def get_payment_type_pie_charts(self) -> list[Figure]:
        return _yearly_pie_charts(self.df, Column.PAYMENT_TYPE, self.redact_values)

    def get_project_pie_charts(self) -> list[Figure]:
        return _yearly_pie_charts(self.df, Column.PROJECT, self.redact_values)

    def get_category_pie_charts(self) -> list[Figure]:
        return _yearly_pie_charts(self.df, Column.CATEGORY, self.redact_values)


def _sum_line_graph(
    df: DataFrame,
    column: Column,
    sort_items: list[Vender | PaymentType | Category | Project],
    title: str,
    redact_values: bool,
) -> Figure:
    values = [item.value for item in sort_items]
    filtered = df[df[column].isin(values)].copy()
    filtered["Date"] = pd.to_datetime(filtered[Column.SHEET_NAME], format="%y%m%d")
    filtered["MonthDate"] = filtered["Date"].dt.to_period("M").dt.to_timestamp()
    filtered["Item"] = filtered[column]

    # Group by month and item
    sum_by_month = filtered.groupby(["MonthDate", "Item"], as_index=False)[
        Column.AMOUNT
    ].sum()
    sum_by_month["Amount"] = sum_by_month[Column.AMOUNT].abs().round(2)
    sum_by_month = sum_by_month.sort_values("MonthDate")  # type: ignore

    # Line plot with multiple traces
    fig = line(
        sum_by_month,
        x="MonthDate",
        y="Amount",
        color="Item",
        title=title,
        template="plotly_dark",
        labels={"MonthDate": "Date", "Amount": "Dollars", "Item": "Category"},
    )
    fig.update_traces(
        hovertemplate="Item: %{fullData.name}<br>Date: %{x|%b %Y}<br>Amount: %{y}<extra></extra>"
    )
    if redact_values:
        _redact_values(fig)
    return fig


def _yearly_pie_charts(
    df: DataFrame,
    column: Column,
    redact_values: bool,
) -> list[Figure]:
    figures: list[Figure] = []
    options = get_options(column)
    df = df.copy()

    df["Date"] = pd.to_datetime(df[Column.SHEET_NAME], format="%y%m%d", errors="coerce")
    df["Year"] = df["Date"].dt.year
    for year in sorted(df["Year"].dropna().unique()):
        year_df = df[df["Year"] == year]
        # Group by the category column (your "options")
        grouped = year_df.groupby(column, as_index=False)[Column.AMOUNT].sum()
        # Optional: filter only valid options
        if options:
            grouped = grouped[grouped[column].isin(options)]
        grouped[Column.AMOUNT] = grouped[Column.AMOUNT].abs().round(2)
        # Skip empty years
        if grouped.empty:
            continue

        total = grouped[Column.AMOUNT].sum()
        percentages = grouped[Column.AMOUNT] / total

        # Build custom text labels
        text = [
            f"{label}" if p >= 0.005 else ""
            for label, p in zip(grouped[column], percentages)
        ]

        fig = pie(
            grouped,
            names=column,
            values=Column.AMOUNT,
            title=f"{column.value} - {year}",
            template="plotly_dark",
        )
        fig.update_traces(
            textinfo="text",
            hovertemplate=(
                "%{label}<br>"
                "Amount: $%{value:.2f}<br>"
                "Percent: %{percent}"
                "<extra></extra>"
            ),
            text=text,
        )
        fig.update_layout(
            margin=dict(t=80, b=20, l=50, r=50),  # Increase top (t) margin for title
            height=700,
            uniformtext_minsize=10,
            uniformtext_mode="hide",
        )
        if redact_values:
            _redact_values(fig)
        figures.append(fig)

    return figures


def _sum_bargraph(
    df: DataFrame,
    column: Column,
    sort_item: Vender | PaymentType | Category | Project,
    redact_values: bool,
) -> Figure:
    fast_food_rows = df[df[column].str.contains(sort_item, case=False, na=False)]

    # Extract year and month
    fast_food_rows["Date"] = pd.to_datetime(
        fast_food_rows[Column.SHEET_NAME], format="%y%m%d"
    )
    fast_food_rows["Year"] = fast_food_rows["Date"].dt.year.astype(str)
    fast_food_rows["MonthNum"] = fast_food_rows["Date"].dt.month
    fast_food_rows["Month"] = fast_food_rows["Date"].dt.strftime("%b")

    # Create group
    sum_by_sheet = fast_food_rows.groupby(
        ["Year", "Month", "MonthNum"], as_index=False
    )[Column.AMOUNT].sum()
    sum_by_sheet["Fast_Food_Amount"] = sum_by_sheet[Column.AMOUNT].abs().round(2)
    sum_by_sheet = sum_by_sheet.sort_values(by=["Year", "MonthNum"])  # type: ignore

    # Line chart with one line per year
    fig1 = bar(
        sum_by_sheet,
        x="Month",
        y="Fast_Food_Amount",
        color="Year",
        title=f"{sort_item.value} Amount by Month",
        template="plotly_dark",
        labels={"Fast_Food_Amount": "Dollars", "Month": "Month", "Year": "Year"},
        category_orders={"Month": MONTHS},
    )
    fig1.update_layout(barmode="stack")
    fig1.update_traces(
        hovertemplate="Year: %{fullData.name}<br>Amount: %{y}<extra></extra>"
    )
    if redact_values:
        _redact_values(fig1)
    return fig1


def _redact_values(fig1: Figure):
    fig1.update_yaxes(showticklabels=False)


def _load_dataframe(workbook_path: Path) -> DataFrame:
    # Load all sheets at once (pandas auto-selects engine)
    sheets: dict[str, DataFrame] = pd.read_excel(workbook_path, sheet_name=None)
    numeric_sheets = {k: v for k, v in sheets.items() if k.isdigit()}
    count = len(numeric_sheets)
    min_val = min(numeric_sheets) if numeric_sheets else None
    max_val = max(numeric_sheets) if numeric_sheets else None
    print(f"{count} sheets spanning from {min_val}-{max_val}")

    # Add sheet name column and combine
    dfs = [
        df.assign(**{Column.SHEET_NAME.value: name})
        for name, df in numeric_sheets.items()
    ]
    return concat(dfs, ignore_index=True)
