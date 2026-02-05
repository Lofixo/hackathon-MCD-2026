import geopandas as gpd
from shapely.geometry import Point
import os

# =========================
# CONFIGURACIÓ PATH
# =========================

base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

GPKG_FILE = os.path.join(data_dir, "section_to_neighbourhood_clean.gpkg")

# =========================
# 1. Carrega GeoPackage amb geometria
# =========================

seccions = gpd.read_file(GPKG_FILE, layer='section_to_neighbourhood')
print("Seccions carregades:", seccions.shape)

# Assegura CRS WGS84
seccions = seccions.to_crs(epsg=4326)

# =========================
# 2. Funció per trobar districte/barri per lat/lon
# =========================

def assign_district(lat, lon):
    point = Point(lon, lat)  # recorda lon, lat per shapely
    # Filtra la secció que conté el punt
    match = seccions[seccions.geometry.contains(point)]
    
    if not match.empty:
        row = match.iloc[0]  # agafa la primera coincidència
        return {
            "districte": row['DISTRICTE'],
            "section": row['SECCIÓ'],
            "district_id": row['district_id'],
            "section_id": row['section_id'],
            "census_tract_INE": row['census_tract_INE'],
            "census_tract_IDESCAT": row['census_tract_IDESCAT'],
            "barri_oficial": row['BARRIS']
        }
    else:
        return {
            "districte": None,
            "section": None,
            "district_id": None,
            "section_id": None,
            "census_tract_INE": None,
            "census_tract_IDESCAT": None,
            "barri_oficial": None
        }
