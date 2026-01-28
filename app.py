import matplotlib.pyplot as plt
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import base64
import io

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import matplotlib
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

location_to_district = {
    'AIIMS': 'SOUTH',
    'Adarsh Nagar': 'NORTH',
    'Akshardham': 'EAST',
    'Ambience Mall': 'OUTSIDE',  # Gurgaon
    'Anand Vihar': 'EAST',
    'Anand Vihar ISBT': 'EAST',
    'Ardee City': 'OUTSIDE',  # Gurgaon
    'Arjangarh': 'SOUTH',
    'Ashok Park Main': 'WEST',
    'Ashok Vihar': 'NORTH WEST',
    'Ashram': 'SOUTH',
    'Aya Nagar': 'SOUTH',
    'Azadpur': 'NORTH WEST',
    'Badarpur': 'SOUTH',
    'Badshahpur': 'OUTSIDE',  # Gurgaon
    'Bahadurgarh': 'OUTSIDE',  # Haryana
    'Barakhamba Road': 'CENTRAL',
    'Basai Dhankot': 'OUTSIDE',  # Faridabad
    'Bhikaji Cama Place': 'SOUTH',
    'Bhiwadi': 'OUTSIDE',  # Rajasthan
    'Botanical Garden': 'OUTSIDE',  # Greater Noida
    'Central Secretariat': 'NEW DELHI',
    'Chanakyapuri': 'CENTRAL',
    'Chandni Chowk': 'CENTRAL',
    'Chhatarpur': 'SOUTH',
    'Chirag Delhi': 'SOUTH',
    'Civil Lines Gurgaon': 'OUTSIDE',  # Gurgaon
    'Connaught Place': 'CENTRAL',
    'Cyber Hub': 'OUTSIDE',  # Gurgaon
    'DLF City Court': 'OUTSIDE',  # Gurgaon
    'DLF Phase 3': 'OUTSIDE',  # Gurgaon
    'Delhi Gate': 'CENTRAL',
    'Dilshad Garden': 'EAST',
    'Dwarka Mor': 'WEST',
    'Dwarka Sector 21': 'SOUTH WEST',
    'Faridabad Sector 15': 'OUTSIDE',  # Faridabad
    'GTB Nagar': 'NORTH',
    'Ghaziabad': 'OUTSIDE',
    'Ghitorni': 'SOUTH',
    'Ghitorni Village': 'SOUTH',
    'Golf Course Road': 'OUTSIDE',  # Gurgaon
    'Govindpuri': 'SOUTH',
    'Greater Kailash': 'SOUTH',
    'Greater Noida': 'OUTSIDE',
    'Green Park': 'SOUTH',
    'Gurgaon Railway Station': 'OUTSIDE',
    'Gurgaon Sector 29': 'OUTSIDE',
    'Gurgaon Sector 56': 'OUTSIDE',
    'Gwal Pahari': 'OUTSIDE',  # Gurgaon
    'Hauz Khas': 'SOUTH',
    'Hauz Rani': 'SOUTH',
    'Hero Honda Chowk': 'OUTSIDE',  # Gurgaon
    'Huda City Centre': 'OUTSIDE',  # Gurgaon
    'IFFCO Chowk': 'OUTSIDE',  # Gurgaon
    'IGI Airport': 'SOUTH WEST',
    'IGNOU Road': 'SOUTH',
    'IIT Delhi': 'SOUTH',
    'IMT Manesar': 'OUTSIDE',  # Haryana
    'INA Market': 'SOUTH',
    'ITO': 'CENTRAL',
    'Inderlok': 'NORTH WEST',
    'India Gate': 'NEW DELHI',
    'Indirapuram': 'OUTSIDE',  # Ghaziabad
    'Indraprastha': 'EAST',
    'Jahangirpuri': 'NORTH WEST',
    'Jama Masjid': 'CENTRAL',
    'Janakpuri': 'WEST',
    'Jasola': 'SOUTH',
    'Jhilmil': 'EAST',
    'Jor Bagh': 'SOUTH',
    'Kadarpur': 'OUTSIDE',  # Gurgaon
    'Kalkaji': 'SOUTH',
    'Kanhaiya Nagar': 'NORTH WEST',
    'Karkarduma': 'EAST',
    'Karol Bagh': 'CENTRAL',
    'Kashmere Gate': 'NORTH',
    'Kashmere Gate ISBT': 'NORTH',
    'Kaushambi': 'OUTSIDE',  # Ghaziabad
    'Keshav Puram': 'NORTH WEST',
    'Khan Market': 'NEW DELHI',
    'Khandsa': 'OUTSIDE',  # Gurgaon
    'Kherki Daula Toll': 'OUTSIDE',  # Gurgaon
    'Kirti Nagar': 'WEST',
    'Lajpat Nagar': 'SOUTH',
    'Lal Quila': 'CENTRAL',
    'Laxmi Nagar': 'EAST',
    'Lok Kalyan Marg': 'NEW DELHI',
    'MG Road': 'OUTSIDE',  # Gurgaon
    'Madipur': 'WEST',
    'Maidan Garhi': 'SOUTH',
    'Malviya Nagar': 'SOUTH',
    'Mandi House': 'CENTRAL',
    'Manesar': 'OUTSIDE',  # Haryana
    'Mansarovar Park': 'EAST',
    'Mayur Vihar': 'EAST',
    'Meerut': 'OUTSIDE',
    'Mehrauli': 'SOUTH',
    'Model Town': 'NORTH',
    'Moolchand': 'SOUTH',
    'Moti Nagar': 'WEST',
    'Mundka': 'WEST',
    'Munirka': 'SOUTH',
    'Narsinghpur': 'OUTSIDE',  # Haryana
    'Nawada': 'SOUTH WEST',
    'Nehru Place': 'SOUTH',
    'Netaji Subhash Place': 'NORTH WEST',
    'New Colony': 'SOUTH',
    'NEW DELHI Railway Station': 'NEW DELHI',
    'Nirman Vihar': 'EAST',
    'Noida Extension': 'OUTSIDE',
    'Noida Film City': 'OUTSIDE',
    'Noida Sector 18': 'OUTSIDE',
    'Noida Sector 62': 'OUTSIDE',
    'Okhla': 'SOUTH',
    'Old Gurgaon': 'OUTSIDE',
    'Paharganj': 'CENTRAL',
    'Palam Vihar': 'OUTSIDE',  # Gurgaon
    'Panchsheel Park': 'SOUTH',
    'Panipat': 'OUTSIDE',
    'Paschim Vihar': 'WEST',
    'Pataudi Chowk': 'OUTSIDE',  # Haryana
    'Patel Chowk': 'NEW DELHI',
    'Peeragarhi': 'WEST',
    'Pitampura': 'NORTH WEST',
    'Pragati Maidan': 'CENTRAL',
    'Preet Vihar': 'EAST',
    'Pulbangash': 'NORTH',
    'Punjabi Bagh': 'WEST',
    'Qutub Minar': 'SOUTH',
    'RK Puram': 'SOUTH',
    'Raj Nagar Extension': 'OUTSIDE',  # Ghaziabad
    'Rajiv Chowk': 'CENTRAL',
    'Rajiv Nagar': 'OUTSIDE',  # Gurgaon
    'Rajouri Garden': 'WEST',
    'Ramesh Nagar': 'WEST',
    'Rithala': 'NORTH WEST',
    'Rohini': 'NORTH WEST',
    'Rohini East': 'NORTH EAST',
    'Rohini West': 'NORTH WEST',
    'Sadar Bazar Gurgaon': 'OUTSIDE',
    'Saidulajab': 'SOUTH',
    'Saket': 'SOUTH',
    'Saket A Block': 'SOUTH',
    'Samaypur Badli': 'NORTH',
    'Sarai Kale Khan': 'SOUTH',
    'Sarojini Nagar': 'SOUTH',
    'Satguru Ram Singh Marg': 'OUTSIDE',  # Gurgaon
    'Seelampur': 'EAST',
    'Shahdara': 'Shahdara',
    'Shastri Nagar': 'NORTH WEST',
    'Shastri Park': 'EAST',
    'Shivaji Park': 'WEST',
    'Sikanderpur': 'OUTSIDE',  # Gurgaon
    'Sohna Road': 'OUTSIDE',  # Gurgaon
    'Sonipat': 'OUTSIDE',
    'South Extension': 'SOUTH',
    'Subhash Chowk': 'OUTSIDE',  # Gurgaon
    'Subhash Nagar': 'WEST',
    'Sultanpur': 'SOUTH',
    'Sushant Lok': 'OUTSIDE',  # Gurgaon
    'Tagore Garden': 'WEST',
    'Tilak Nagar': 'WEST',
    'Tis Hazari': 'NORTH',
    'Tughlakabad': 'SOUTH',
    'Udyog Bhawan': 'NEW DELHI',
    'Udyog Vihar': 'OUTSIDE',  # Gurgaon
    'Udyog Vihar Phase 4': 'OUTSIDE',
    'Uttam Nagar': 'WEST',
    'Vaishali': 'OUTSIDE',  # Ghaziabad
    'Vasant Kunj': 'SOUTH',
    'Vatika Chowk': 'OUTSIDE',  # Gurgaon
    'Vidhan Sabha': 'NORTH',
    'Vinobapuri': 'SOUTH',
    'Vishwavidyalaya': 'NORTH',
    'Welcome': 'EAST',
    'Yamuna Bank': 'EAST'
}


def get_admin_region(place):
    return location_to_district.get(place.title().strip(), "UNKNOWN")


def transform_column(series: pd.Series) -> pd.Series:
    return series.apply(get_admin_region)


df["Pickup region"] = transform_column(df["Pickup Location"])
df["Drop region"] = transform_column(df["Drop Location"])

# Delhi district info, for map
DISTRICT_SHP = "input/DISTRICT_BOUNDARY.shp"
gdf = gpd.read_file(DISTRICT_SHP)

# Clean column values
gdf["District"] = gdf["District"].str.replace(">", "").str.strip()
gdf["STATE"] = gdf["STATE"].str.replace(">", "").str.strip()

# Keep only Delhi, project to metric CRS (UTM‑44N)
DELHI = gdf[gdf["STATE"] == "DELHI"].to_crs(epsg=32644).copy()
DELHI["centroid"] = DELHI.geometry.centroid


def build_flow_gdf(df_filtered: pd.DataFrame) -> gpd.GeoDataFrame:
    flows = (
        df_filtered
        .groupby(["Pickup region", "Drop region"])
        .size()
        .reset_index(name="volume")
    )
    valid_names = set(DELHI["District"])
    flows = flows[
        flows["Pickup region"].isin(valid_names) &
        flows["Drop region"].isin(valid_names)
    ].reset_index(drop=True)

    lookup = DELHI.set_index("District")["centroid"]

    def make_line(row):
        origin_pt = lookup[row["Pickup region"]]
        dest_pt = lookup[row["Drop region"]]
        return LineString([origin_pt, dest_pt])

    flows["geometry"] = flows.apply(make_line, axis=1)
    gdf_flows = gpd.GeoDataFrame(flows,
                                 geometry="geometry",
                                 crs=DELHI.crs)

    return gdf_flows


def render_flow_map(gdf_flows: gpd.GeoDataFrame) -> str:
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    DELHI.plot(ax=ax,
               edgecolor="gray",
               facecolor="#f0f0f0",
               linewidth=0.8)

    # Scale line width by volume
    max_w, min_w = 8, 0.5
    vmin, vmax = gdf_flows["volume"].min(), gdf_flows["volume"].max()
    if vmax == vmin:
        lw = pd.Series([max_w] * len(gdf_flows))
    else:
        lw = (gdf_flows["volume"] - vmin) / \
            (vmax - vmin) * (max_w - min_w) + min_w

    gdf_flows.plot(
        ax=ax,
        linewidth=lw,
        alpha=0.7,
        cmap="plasma",
        column="volume",
        legend=False  # legend will be added manually later (optional),
    )

    for _, r in DELHI.iterrows():
        ax.text(r.centroid.x, r.centroid.y,
                r.District,
                ha="center", va="center", fontsize=9,
                bbox=dict(facecolor="white", edgecolor="none",
                          pad=0.3, alpha=0.7))

    ax.set_axis_off()
    fig.suptitle("Uber rides between Delhi districts", fontsize=16)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)          # free memory
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()

    html_str = f"""
    <html>
      <head>
        <style>
          body {{ margin:0; padding:0; overflow:hidden; background:#fafafa; }}
        </style>
      </head>
      <body>
        <img src="data:image/png;base64,{img_base64}"
             style="width:100%;height:auto;display:block;margin:0 auto;"/>
      </body>
    </html>
    """
    return html_str


def make_cell(children):
    return dbc.Card(
        dbc.CardBody([
            html.Div(children)
        ]),
        className="shadow mb-4",
        style={"borderRadius": "10px", "border": "1px solid #444"}
    )
# %% md
# DASH


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
