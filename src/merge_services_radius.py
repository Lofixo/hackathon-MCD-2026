"""
merge_services_binaries.py

This script enriches the Girona rental dataset with binary service accessibility features.

- For each rental, we create binary columns indicating whether there is at least one service
  of a given category within a specified radius.
- Categories: education, food, health, mobility, public_service
- Radius is configurable (meters).
"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# =========================
# CONFIGURATION PATHS
# =========================
base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

RENT_CSV = os.path.join(data_dir, "interim", "girona_for_rent_with_energy.csv")
SERVICES_CSV = os.path.join(data_dir, "initial", "girona_services.csv")
OUTPUT_CSV = os.path.join(data_dir, "interim", "girona_for_rent_with_services_binary.csv")

# =========================
# PARAMETERS
# =========================
RADIUS_M = 500  # radius in meters
CATEGORIES = ["education", "food", "health", "mobility", "public_service"]

# =========================
# LOAD DATA
# =========================
rent = pd.read_csv(RENT_CSV)
services = pd.read_csv(SERVICES_CSV)

# Create geometries
rent_gdf = gpd.GeoDataFrame(rent, geometry=gpd.points_from_xy(rent.lon, rent.lat), crs="EPSG:4326")
services_gdf = gpd.GeoDataFrame(services, geometry=gpd.points_from_xy(services.lon, services.lat), crs="EPSG:4326")

# Transform to metric CRS for distance calculation
rent_gdf = rent_gdf.to_crs(epsg=3857)
services_gdf = services_gdf.to_crs(epsg=3857)

# =========================
# FUNCTION TO COMPUTE BINARY SERVICES
# =========================
def binary_services(rental_point, services_gdf, radius_m=250, categories=CATEGORIES):
    buffer = rental_point.buffer(radius_m)
    within_buffer = services_gdf[services_gdf.geometry.within(buffer)]
    
    result = {}
    for cat in categories:
        cat_count = within_buffer[within_buffer['category'] == cat].shape[0]
        result[f'has_{cat}_within_{radius_m}m'] = 1 if cat_count > 0 else 0
    return pd.Series(result)

# =========================
# APPLY FUNCTION
# =========================
services_binary = rent_gdf.geometry.apply(lambda x: binary_services(x, services_gdf, radius_m=RADIUS_M, categories=CATEGORIES))

# Combine with rental dataset
rent_final = pd.concat([rent, services_binary], axis=1)

# =========================
# SAVE FINAL DATASET
# =========================
rent_final.to_csv(OUTPUT_CSV, index=False)
print(f"✔ Dataset with binary service accessibility features saved to: {OUTPUT_CSV}")
