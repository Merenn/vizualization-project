
import geopandas as gpd

# 1️⃣ Load the shapefile
in_path  = "DISTRICT_BOUNDARY.shp"
gdf = gpd.read_file(in_path)

filtered = gdf[gdf["STATE"] == "DELHI"]

# 4️⃣ Write out a new shapefile
out_path = "DISTRICT_BOUNDARY.shp"
filtered.to_file(out_path, driver="ESRI Shapefile")

print(f"Saved {len(filtered)} features to {out_path}")