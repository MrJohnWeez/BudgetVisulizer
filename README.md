
# Budget Visualizer

Quick python project that:
- Grabs budget workbook data
- Parses data using Pandas
- Generate webpage of data using Dash
- Allows for Plotly plots and useful labels.

# Setup

1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)
2. Open terminal and run `uv sync`

# Command Structure

`uv run app.py --file Path_To_Excel_file.xlsx --build`

- `--file` path of excel file to parse
- `--build` create zip file of html page to download

# Provided Synthetic Example

`uv run app.py --file Assets/ExampleBudget.xlsx`

or modify dev/run scripts (linux or windows)

Example Budget provided was AI generated to avoid personal information but still provide a plausible data log.

![Example car trailer costs plot](Docs/Images/car-trailer-costs.png)

![Example category plot](Docs/Images/category.png)

![Example food costs plot](Docs/Images/food-costs.png)

![Example house projects plot](Docs/Images/house-projects.png)

![Example image plot](Docs/Images/image.png)

![Example payment-type plot](Docs/Images/payment-type.png)

![Example project plot](Docs/Images/project.png)

![Example stores plot](Docs/Images/stores.png)

![Example subscriptions plot](Docs/Images/subscriptions.png)

![Example total spent on house plot](Docs/Images/total-spent-on-house.png)

![Example utility cost plot](Docs/Images/utility-cost.png)

![Example vender plot](Docs/Images/vender.png)
