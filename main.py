import plotly.express as px
from pandas import DataFrame, ExcelFile, read_excel, concat
from plotly.subplots import make_subplots

WORKBOOK_NAME = "Assets/Budget.xlsx"

# Columns
SHEET_NAME = "Sheet Name"
ENTRY = "Entry"
AMOUNT = "Amount"
VENDER = "Vender"
PAYMENT_TYPE = "Payment Type"
CATEGORY = "Category"
PROJECT = "Project"


def main():
    xls = ExcelFile(WORKBOOK_NAME, engine="openpyxl")
    numeric_sheets = [name for name in xls.sheet_names if name.isdigit()]  # pyright: ignore[reportAttributeAccessIssue]
    count = len(numeric_sheets)
    min_val = min(numeric_sheets) if numeric_sheets else None
    max_val = max(numeric_sheets) if numeric_sheets else None
    print(f"{count} sheets spanning from {min_val}-{max_val}")

    # Load each sheet, add 'sheet_name' as the first column
    dfs = []
    for name in numeric_sheets:
        df = read_excel(xls, sheet_name=name)
        df.insert(0, SHEET_NAME, name)  # insert at position 0
        dfs.append(df)

    # Combine all into a single DataFrame
    df = concat(dfs, ignore_index=True)
    print(df.head())
    print(get_unique_venders(VENDER, df))

    # Filter rows containing "Fast Food"
    fast_food_rows = df[df[VENDER].str.contains("Fast Food", case=False, na=False)]
    sum_by_sheet = fast_food_rows.groupby(SHEET_NAME, as_index=False)[AMOUNT].sum()
    sum_by_sheet[AMOUNT] = sum_by_sheet[AMOUNT].round(2)
    sum_by_sheet["Amount_abs"] = sum_by_sheet[AMOUNT].abs()
    fig = px.bar(
        sum_by_sheet,
        x=SHEET_NAME,
        y="Amount_abs",
        color="Amount_abs",
        color_continuous_scale="Reds",  # light red = low, dark red = high
        title="Fast Food Amount by Month",
        template="plotly_dark",
    )
    fig.show()

    # Create a subplot figure with 1 row, 2 columns

    subplots = make_subplots(
        rows=1, cols=2, subplot_titles=("Fast Food Spending", "Other Chart")
    )

    # Add the bar traces from fig1 and fig2
    for trace in fig.data:
        subplots.add_trace(trace, row=1, col=1)
    for trace in fig.data:
        subplots.add_trace(trace, row=1, col=2)

    # Update layout if needed
    subplots.update_layout(height=500, width=1000, showlegend=False)
    subplots.show()


def get_unique_venders(column: str, df: DataFrame) -> list[str]:
    return list(df[column].unique())


if __name__ == "__main__":
    main()
