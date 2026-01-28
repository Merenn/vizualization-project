import matplotlib.pyplot as plt
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import matplotlib
from utils import transform_column, build_flow_gdf, render_flow_map

matplotlib.use("Agg")

THEME = "plotly_dark"

# Dataset loading and preprocesing ----------------------------------------------------------
df = pd.read_csv("ncr_ride_bookings.csv", parse_dates=["Date"])

# Change all object types to categorical types
for col in df.select_dtypes(include="object"):
    df[col] = df[col].astype("category")

# Change Cancelled Rides by Driver / Customer and Incomplete Rides to boolean type
df["Cancelled Rides by Customer"] = df["Cancelled Rides by Customer"].notna().astype("bool")
df["Cancelled Rides by Driver"] = df["Cancelled Rides by Driver"].notna().astype("bool")
df["Incomplete Rides"] = df["Incomplete Rides"].notna().astype("bool")

# Add average speed attribute in km/h
df["Avg Speed"] = df["Ride Distance"] / (df["Avg CTAT"] / 60)

# Add weekday and hour columns
df["Weekday"] = df["Date"].dt.day_name()
df["Hour"] = df["Time"].str.split(":").str[0]

df["Pickup region"] = transform_column(df["Pickup Location"])
df["Drop region"] = transform_column(df["Drop Location"])

def make_cell(children):
    return dbc.Card(
        dbc.CardBody([
            html.Div(children)
        ]),
        className="shadow mb-4",
        style={"borderRadius": "10px", "border": "1px solid #444"}
    )

# DASH ---------------------------------------------------------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "margin": "2rem"},
    children=[
        # title --------------------------------------------------------------------------------------------
        html.H1("Uber Rides Data"),
        html.P([
            "The dataset contains rides from 2024 from New Delhi, India. It was taken from ",
            html.A(
                "this Kaggle dataset",
                href="https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard",
                target="_blank"
            ),
            "."
        ]),
        html.Hr(style={"margin-bottom": "10px"}),

        # main part -----------------------------------------------------------------------------------------
        html.Div(children=[
            dbc.Row([
                dbc.Col(children=[
                    make_cell([html.Div(  # rides count
                        html.H2(id="rides-count"),
                        id="rides-count-container"
                    ),
                        html.Div(  # Date range picker div
                        children=[
                            html.Label("Date Range", style={"margin": "5px"}),
                            dcc.DatePickerRange(
                                id="date-range-picker",
                                min_date_allowed=pd.Timestamp("2024-01-01"),
                                max_date_allowed=pd.Timestamp("2024-12-31"),
                                start_date=pd.Timestamp("2024-01-01"),
                                end_date=pd.Timestamp("2024-12-31"),
                                display_format="YYYY‑MM‑DD",
                            ),
                        ],
                        style={"margin": "10px"}
                    ),
                        html.Div(
                        children=[  # Vehicle type checkboxes div
                            html.Label("Vehicle type"),
                            dbc.Checklist(
                                options=[
                                    {"label": "Auto (Auto-rickshaw)",
                                     "value": "Auto"},
                                    {"label": "Go Mini (Low-cost small hatchbacks)",
                                     "value": "Go Mini"},
                                    {"label": "Go Sedan (Standard sedans)",
                                     "value": "Go Sedan"},
                                    {"label": "Bike (Motorcycles)",
                                     "value": "Bike"},
                                    {"label": "Premier Sedan (Premium/luxury sedans)",
                                     "value": "Premier Sedan"},
                                    {"label": "eBike (Electric motorcycle rides)",
                                     "value": "eBike"},
                                    {"label": "Uber XL (Larger vehicles - SUVs or 6–7 seaters)",
                                     "value": "Uber XL"}
                                ],
                                value=["Auto", "Go Mini", "Go Sedan", "Bike",
                                       "Premier Sedan", "eBike", "Uber XL"],
                                id="vehicle-types-checklist",
                                switch=True
                            )
                        ],
                        style={"margin": "20px 0 0 0"}
                    )]),

                    make_cell([html.H3("Vehicle types barchart"),
                              dcc.Graph(id="vehicle-types-barchart")])
                ], width=6),
                dbc.Col(children=[
                    make_cell([
                        html.H3("Ride Flow Map Between Delhi Districts"),
                        html.Div(
                            id="flow-map-container",
                            children=[
                                html.Iframe(
                                    id="flow-map",
                                    srcDoc="",  # Filled by callback below
                                    style={
                                        "width": "100%",
                                        "height": "52rem",
                                        "border": "1px solid #ddd",
                                        "borderRadius": "5px"
                                    }
                                )
                            ]
                        )
                    ]
                    ),
                ], width=6)
            ]),


            dbc.Row([
                dbc.Col([
                    make_cell([
                        html.Div(  # payment methods piechart
                            children=[
                                html.H3("Payment methods piechart"),
                                dcc.Graph(id="payment-piechart")
                            ],
                            id="payment-piechart-container",
                        )])
                ], width=5),
                dbc.Col([
                    make_cell([
                        html.Div(  # Rides volume area chart
                            children=[
                                html.H3("Rides volume area chart"),
                                html.Label("Group by", style={"display": "inline"}),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "Date", "value": "Date"},
                                        {"label": "Weekday", "value": "Weekday"},
                                        {"label": "Hour", "value": "Hour"},
                                    ],
                                    value="Date",
                                    id="areachart-group-radio",
                                    inline=True,
                                    switch=True,
                                    style={"display": "inline", "margin-left": "10px"},
                                ),
                                dcc.Graph(id="areachart")
                            ],
                            id="areachart-container",
                        )])
                ], width=7),
            ]),
            make_cell(html.Div(  # Scatterplot
                children=[
                    html.H3("Numerical attributes scatterplot"),
                    dbc.Row([
                        dbc.Col([html.Label("X-axis:"), dbc.Select(
                            options=[
                                {"label": "Average Time - driver to pickup location",
                                 "value": "Avg VTAT"},
                                {"label": "Average Time - pickup to destination",
                                 "value": "Avg CTAT"},
                                {"label": "Booking Value",
                                 "value": "Booking Value"},
                                {"label": "Ride Distance",
                                 "value": "Ride Distance"},
                                {"label": "Driver Ratings",
                                 "value": "Driver Ratings"},
                                {"label": "Customer Ratings",
                                 "value": "Customer Rating"},
                                {"label": "Average Speed",
                                 "value": "Avg Speed"},
                            ],
                            value="Ride Distance",
                            id="scatterplot-x-axis",
                            className="bg-dark text-white border-secondary",
                        )], width=4),
                        dbc.Col([html.Label("Y-axis:"), dbc.Select(
                            options=[
                                {"label": "Average Time - driver to pickup location",
                                 "value": "Avg VTAT"},
                                {"label": "Average Time - pickup to destination",
                                 "value": "Avg CTAT"},
                                {"label": "Booking Value",
                                 "value": "Booking Value"},
                                {"label": "Ride Distance",
                                 "value": "Ride Distance"},
                                {"label": "Driver Ratings",
                                 "value": "Driver Ratings"},
                                {"label": "Customer Ratings",
                                 "value": "Customer Rating"},
                                {"label": "Average Speed",
                                 "value": "Avg Speed"},
                            ],
                            value="Avg Speed",
                            id="scatterplot-y-axis",
                            className="bg-dark text-white border-secondary"
                        )], width=4),
                    ]),
                    dcc.Graph(id="scatterplot", style={"margin-top": "1rem"}),
                ],
                id="scatterplot-container",
                style={"margin": "20px 0"}
            )),
        ])
    ],
)

# Callbacks --------------------------------------------------------------------------

# callback for total rides text


@app.callback(
    Output("rides-count", "children"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value")
)
def update_total_rides(start_date, end_date, vehicle_types):
    count = len(df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))
    ])

    return f"Total rides: {count}"


# callback for vehicle type barchart
@app.callback(
    Output("vehicle-types-barchart", "figure"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value")
)
def update_vehicle_types_barchart(start_date, end_date, vehicle_types):
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))
    ].groupby("Vehicle Type", observed=True).size().reset_index(name="Count")

    fig = px.bar(
        filtered_df,
        x="Vehicle Type",
        y="Count",
        color="Vehicle Type",
        template=THEME
    )

    y_limit = (filtered_df["Count"].max() // 5_000 + 1) * 5000
    fig.update_layout(
        yaxis=dict(range=[0, y_limit], title="Count"),
        margin=dict(t=40, l=20, r=20, b=20)
    )
    return fig


# callback for scatterplot
@app.callback(
    Output("scatterplot", "figure"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value"),
    Input("scatterplot-x-axis", "value"),
    Input("scatterplot-y-axis", "value")
)
def update_scatterplot(start_date, end_date, vehicle_types, x_axis_attribute, y_axis_attribute):
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))
    ].dropna(subset=[x_axis_attribute, y_axis_attribute])  # drop any row where either is NaN

    fig = px.scatter(
        filtered_df,
        x=x_axis_attribute,
        y=y_axis_attribute,
        template=THEME,
    )

    fig.update_layout(
        margin=dict(t=40, l=20, r=20, b=20)
    )

    fig.update_traces(
        marker=dict(
            size=4,
            opacity=0.3,
            line=dict(width=0)
        )
    )

    return fig


# callback for payment method piechart
@app.callback(
    Output("payment-piechart", "figure"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value"),
)
def update_payment_piechart(start_date, end_date, vehicle_types):
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))
    ].groupby("Payment Method", observed=True).agg(
        Count=("Payment Method", "size"),
        Total_Revenue=("Booking Value", "sum")
    ).reset_index()

    fig = px.pie(
        filtered_df,
        names="Payment Method",
        values="Count",
        hole=0.5,
        template=THEME
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>{int(filtered_df['Total_Revenue'].sum()):,} INR</b><br>Total Revenue <br>",
                x=0.5,
                y=0.5,
                font_size=18,
                showarrow=False,
                align="center",
            )
        ],
        margin=dict(t=40, l=20, r=20, b=20)
    )

    return fig


# callback for rides volume area chart
@app.callback(
    Output("areachart", "figure"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value"),
    Input("areachart-group-radio", "value")
)
def update_areachart(start_date, end_date, vehicle_types, grouping):
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))
    ].groupby(grouping, observed=True).agg(
        completed=("Booking Status", lambda x: (x == "Completed").sum()),
        not_completed=("Booking Status", lambda x: (x != "Completed").sum())
    ).reset_index()

    filtered_df.columns = [grouping, 'Completed', 'Incomplete or Cancelled']

    fig = px.area(
        filtered_df,
        x=grouping,
        y=filtered_df.columns[1:],
        labels={"value": "Number of Rides", "variable": "Booking Status"},
        template=THEME
    )

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
        hovermode="x unified")

    return fig


@app.callback(
    Output("flow-map", "srcDoc"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("vehicle-types-checklist", "value")
)
def update_flow_map(start_date, end_date, vehicle_types):
    filtered_df = df[
        (df["Date"] >= start_date) &
        (df["Date"] <= end_date) &
        (df["Vehicle Type"].isin(vehicle_types))]
    gdf_flows = build_flow_gdf(filtered_df)

    html_map = render_flow_map(gdf_flows)
    return html_map


# Running the app ------------------------------------------------------------
if __name__ == '__main__':
    app.run(jupyter_mode="external", debug=True)  # inline/tab/external
