import pandas as pd
import base64
import io
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib as mpl

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
    'Udyog Vihar': 'OUTSIDE',
    'Udyog Vihar Phase 4': 'OUTSIDE',
    'Uttam Nagar': 'WEST',
    'Vaishali': 'OUTSIDE',
    'Vasant Kunj': 'SOUTH',
    'Vatika Chowk': 'OUTSIDE',
    'Vidhan Sabha': 'NORTH',
    'Vinobapuri': 'SOUTH',
    'Vishwavidyalaya': 'NORTH',
    'Welcome': 'EAST',
    'Yamuna Bank': 'EAST'
}

DISTRICT_SHP = "input/DISTRICT_BOUNDARY.shp"
gdf = gpd.read_file(DISTRICT_SHP)
gdf["District"] = gdf["District"].str.replace(">", "").str.strip()
gdf["STATE"]    = gdf["STATE"].str.replace(">", "").str.strip()
DELHI = gdf[gdf["STATE"] == "DELHI"].to_crs(epsg=32644).copy()
DELHI["centroid"] = DELHI.geometry.centroid

def get_admin_region(place):
    return location_to_district.get(place.title().strip(), "UNKNOWN")

def transform_column(series: pd.Series) -> pd.Series:
    return series.apply(get_admin_region)

def build_flow_gdf(df_filtered: pd.DataFrame) -> gpd.GeoDataFrame:
    if df_filtered.empty:
        return gpd.GeoDataFrame(
            columns=["Pickup region", "Drop region", "volume", "geometry"],
            crs=DELHI.crs,
            geometry=[],
        )
    flows = (
        df_filtered
        .groupby(["Pickup region", "Drop region"])
        .size()
        .reset_index(name="volume")
    )
    valid_names = set(DELHI["District"])
    flows = flows[
        flows["Pickup region"].isin(valid_names)
        & flows["Drop region"].isin(valid_names)
    ].reset_index(drop=True)

    lookup = DELHI.set_index("District")["centroid"]

    def make_line(row):
        origin_pt = lookup[row["Pickup region"]]
        dest_pt = lookup[row["Drop region"]]
        return LineString([origin_pt, dest_pt])

    flows["geometry"] = flows.apply(make_line, axis=1)
    return gpd.GeoDataFrame(flows, geometry="geometry", crs=DELHI.crs)


def render_flow_map(gdf_flows: gpd.GeoDataFrame) -> str:
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    DELHI.plot(
        ax=ax,
        edgecolor="gray",
        facecolor="#f0f0f0",
        linewidth=0.8,
    )

    max_w, min_w = 8, 0.5
    vmin, vmax = gdf_flows["volume"].min(), gdf_flows["volume"].max()

    if vmax == vmin:
        lw = pd.Series([max_w] * len(gdf_flows))
    else:
        lw = (
            (gdf_flows["volume"] - vmin) / (vmax - vmin) * (max_w - min_w) + min_w
        )

    cmap = "plasma"
    gdf_flows.plot(
        ax=ax,
        linewidth=lw,
        alpha=0.7,
        cmap=cmap,
        column="volume",
        legend=False,
    )

    for _, r in DELHI.iterrows():
        ax.text(
            r.centroid.x,
            r.centroid.y,
            r.District,
            ha="center",
            va="center",
            fontsize=9,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.3, alpha=0.7),
        )

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(
        sm,
        ax=ax,
        orientation="vertical",
        fraction=0.045,
        pad=0.04,
    )
    cbar.set_label("Ride volume (number of trips)", size=10)

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