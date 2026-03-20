from enum import Enum
from pathlib import Path

from dash.html import Col
from pandas import DataFrame, ExcelFile, concat, read_excel
from plotly.graph_objs import Figure
from plotly.express import line, bar, pie
import pandas as pd


class Column(str, Enum):
    ENTRY = "Entry"
    AMOUNT = "Amount"
    VENDER = "Vender"
    PAYMENT_TYPE = "Payment Type"
    CATEGORY = "Category"
    PROJECT = "Project"
    SHEET_NAME = "Sheet Name"


class Vender(str, Enum):
    HOME_DEPOT = "Home Depot"
    AMAZON = "Amazon"
    KROGER = "Kroger"
    LOWES = "Lowes"
    MENARDS = "Menards"
    WALMART = "Walmart"
    SAMS = "Sams"
    STAPLES = "Staples"
    TARGET = "Target"
    EUFY = "Eufy"
    BANK = "Bank"
    NET10 = "Net10"
    SPOTIFY = "Spotify"
    DUKE_ENERGY = "Duke Energy"
    GCWW = "GCWW"
    ALTAFIBER = "Altafiber"
    GOVERNMENT = "Goverment"
    AAA = "AAA"
    PARENTS = "Parents"
    RUMPKE = "Rumpke"
    UDF = "UDF"
    BP = "BP"
    FAST_FOOD = "Fast Food"
    OTHER = "Other"
    WALGREENS = "Walgreens"
    WIDTHHOLD = "Widthhold"
    PEACOCK_TV = "Peacock TV"
    COSTCO = "Costco"
    US_MOBILE = "USMobile"
    NETFLIX = "Netflix"
    STEAM = "Steam"
    UNITY = "Unity"
    RANDOM_STORES = "Random Stores"
    GAME_STORES = "Game Stores"
    EYE_CARE = "Eye Care"
    KOHLS = "Kohl's"
    HARBOR_FREIGHT_TOOLS = "Harbor Freight Tools"
    BAKER_CABINETS = "Baker Cabinets"
    DISNEY_PLUS = "Diseny Plus"
    CABINETS_COM = "Cabinets com"


class PaymentType(str, Enum):
    CAPITALONE_MASTER = "CapitalOne Master"
    GEVISA = "GEVisa"
    ECHECK = "ECheck"
    CHECK = "Check"
    DIRECT_DEPOSIT = "Direct Deposit"
    WIDTHHOLD = "Widthhold"


class Category(str, Enum):
    HOUSE_IMPROVEMENT = "House/Improvement"
    FOOD = "Food"
    TAKEOUT = "Takeout"
    GAS = "Gas"
    ELECTRIC = "Eletric"
    WATER_SEWAGE = "Water/Sewage"
    INTERNET = "Internet"
    TOOLS = "Tools"
    CAR_GAS = "Car/Gas"
    WANTS = "Wants"
    INSURANCE = "Insurance"
    TAX = "Tax"
    HOUSEHOLD_ITEMS = "Household Items"
    HEALTH = "Health"
    MORTGAGE = "Mortgage"
    SAVINGS = "Savings"
    INCOME = "Income"
    TRASH = "Trash"
    SUBSCRIPTIONS = "Subscriptions"
    APPLIANCES = "Appliances"
    TRAILER = "Trailer"
    CONSUMABLE = "Consumable"
    FURNITURE = "Furniture"
    GIFT = "Gift"
    GAME_DEV = "Game Dev"
    SOCIAL = "Social"
    DONATION = "Donation"
    GAMBLE = "Gamble"


class Project(str, Enum):
    HOUSE_PAINT = "House Paint"
    HOUSE_ROOF = "House Roof"
    HOUSE_YARD = "House Yard"
    MAIN_BATHROOM = "Main Bathroom"
    ATTIC_CLEANUP = "Attic Cleanup"
    KITCHEN_REMODEL = "Kitchen Remodel"
    MASTER_BEDROOM_BATH = "Master Bedroom/Bath"
    WINDOWS = "Windows"
    BASEMENT_SINK = "Basement Sink"
    FAMILY_ROOM_CLEANUP = "Family Room Cleanup"
    ROOM_IMPROVEMENT = "Room Improvement"
    SECURITY = "Security"
    ELETRIC = "Eletric"
    BASEMENT_CLEANUP = "Basement Cleanup"
    GUTTER_FIX = "Gutter Fix"
    GARAGE_LIGHTING = "Garage Lighting"
    LIVINGROOM_MOLDING_LIGHTING = "Livingroom Molding Lighting"
    LIVINGROOM_MOLDING = "Livingroom Molding"
    GENERAL_PLUMBING = "General Plumbing"
    BASEMENT_REMODEL = "Basement Remodel"


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
        plots = [_sum_bargraph(self.df, Column.VENDER, Vender.FAST_FOOD)]
        plots += _yearly_pie_charts(self.df, Column.VENDER)
        return plots


def _yearly_pie_charts(
    df: DataFrame,
    column: Column,
) -> list[Figure]:
    figures: list[Figure] = []
    options = _get_options(column)
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
        fig = pie(
            grouped,
            names=column,
            values=Column.AMOUNT,
            title=f"{column} Breakdown - {year}",
            template="plotly_dark",
        )
        fig.update_traces(
            textinfo="label",
            hovertemplate=(
                f"{column}: %{{label}}<br>"
                "Amount: $%{value:.2f}<br>"
                "Percent: %{percent}"
                "<extra></extra>"
            ),
        )
        figures.append(fig)

    return figures


def _get_options(column: Column) -> list[str]:
    match column:
        case Column.VENDER:
            return [v.value for v in Vender]
        case Column.PAYMENT_TYPE:
            return [p.value for p in PaymentType]
        case Column.CATEGORY:
            return [c.value for c in Category]
        case Column.PROJECT:
            return [p.value for p in Project]
    return []


def _sum_bargraph(
    df: DataFrame,
    column: Column,
    sort_item: Vender | PaymentType | Category | Project,
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
        title=f"{sort_item} Amount by Month",
        template="plotly_dark",
        labels={
            "Fast_Food_Amount": "Dollars",
            "Month": "Month",
            "Year": "Year",
        },
        category_orders={"Month": MONTHS},
    )

    fig1.update_layout(barmode="stack")
    fig1.update_traces(
        hovertemplate="Year: %{fullData.name}<br>Amount: %{y}<extra></extra>"
    )
    return fig1


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
        df.insert(0, Column.SHEET_NAME.value, name)
        dfs.append(df)

    # Combine all into a single DataFrame
    return concat(dfs, ignore_index=True)


def _get_unique_items(column: str, df: DataFrame) -> list[str]:
    return list(df[column].unique())
