from pathlib import Path

from pandas import DataFrame, ExcelFile, concat, read_excel
from plotly.graph_objs import Figure
from plotly.express import bar, line
import pandas as pd

# Columns
SHEET_NAME = "Sheet Name"
ENTRY = "Entry"
AMOUNT = "Amount"
VENDER = "Vender"
PAYMENT_TYPE = "Payment Type"
CATEGORY = "Category"
PROJECT = "Project"

# Filters
HOUSE_IMPROVEMENT = "House/Improvement"

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


class DataLoader:
    def __init__(self, workbook_path: Path) -> None:
        self.df = _load_dataframe(workbook_path)

    def get_plots(self) -> list[Figure]:
        fast_food_rows = self.df[
            self.df[VENDER].str.contains("Fast Food", case=False, na=False)
        ]

        sum_by_sheet = fast_food_rows.groupby(SHEET_NAME, as_index=False)[AMOUNT].sum()
        sum_by_sheet[AMOUNT] = sum_by_sheet[AMOUNT].round(2)
        sum_by_sheet["Fast_Food_Amount"] = sum_by_sheet[AMOUNT].abs()

        # Convert YYMMDD → datetime
        sum_by_sheet["Date"] = pd.to_datetime(sum_by_sheet[SHEET_NAME], format="%y%m%d")

        # Extract year + month
        sum_by_sheet["Year"] = sum_by_sheet["Date"].dt.year
        sum_by_sheet["MonthNum"] = sum_by_sheet["Date"].dt.month
        sum_by_sheet["Month"] = sum_by_sheet["Date"].dt.strftime("%b")

        # Sort by year then month number
        sum_by_sheet = sum_by_sheet.sort_values(by=["Year", "MonthNum"])  # type: ignore

        # Line chart with one line per year
        fig1 = line(
            sum_by_sheet,
            x="Month",
            y="Fast_Food_Amount",
            color="Year",
            markers=True,
            title="Fast Food Amount by Month",
            template="plotly_dark",
            labels={"Fast_Food_Amount": "Dollars", "Month": "Month", "Year": "Year"},
            category_orders={"Month": MONTHS},
        )
        return [fig1]


def _load_dataframe(workbook_path: Path) -> DataFrame:
    xls = ExcelFile(workbook_path, engine="openpyxl")
    numeric_sheets = [name for name in xls.sheet_names if name.isdigit()]  # pyright: ignore[reportAttributeAccessIssue]
    count = len(numeric_sheets)
    min_val = min(numeric_sheets) if numeric_sheets else None
    max_val = max(numeric_sheets) if numeric_sheets else None
    print(f"{count} sheets spanning from {min_val}-{max_val}")

    # Load each sheet, add 'sheet_name' as the first column
    dfs = []
    for name in numeric_sheets:
        df = read_excel(xls, sheet_name=name)
        df.insert(0, SHEET_NAME, name)
        dfs.append(df)

    # Combine all into a single DataFrame
    return concat(dfs, ignore_index=True)


def _get_unique_items(column: str, df: DataFrame) -> list[str]:
    return list(df[column].unique())
