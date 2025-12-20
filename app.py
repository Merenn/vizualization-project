import dash
from dash import dcc, html
import pandas as pd

app = dash.Dash(__name__)
server = app.server

try:
    df = pd.read_csv("ncr_ride_bookings.csv")
    print("Data loaded successfully.")
except FileNotFoundError:
    print("File 'ncr_ride_bookings.csv' not found – exiting.")
    exit(1)

min_allowed_date = pd.Timestamp("2024-01-01")
max_allowed_date = pd.Timestamp("2024-12-31")

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "2rem"},
    children=[
        html.H1("Uber Rides Data"),

        html.Div(
            [
                html.Label("Select a date range (within a single year):"),
                dcc.DatePickerRange(
                    id="date-range-picker",
                    min_date_allowed=min_allowed_date,
                    max_date_allowed=max_allowed_date,
                    start_date=min_allowed_date,
                    end_date=max_allowed_date,
                    display_format="YYYY‑MM‑DD",
                ),
            ],
            style={"marginBottom": "1.5rem"},
        ),

        dcc.Store(id="filtered-data-store"),

        html.H3("Filtered data preview"),
        dcc.Markdown(
            df.head().to_markdown(index=False),  # pandas → markdown table
            style={"whiteSpace": "pre-wrap"}
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
