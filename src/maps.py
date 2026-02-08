import geopandas as gpd
import os

# =========================
# CONFIGURACIÓ DE PATHS
# =========================

base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

SECCIONS_DIR = os.path.join(data_dir, "seccions_girona")
BARRIS_DIR = os.path.join(data_dir, "barris_girona")
SECTORS_DIR = os.path.join(data_dir, "sectors_girona") 

SECCIONS_FILE = os.path.join(SECCIONS_DIR, "Seccions.shp")
BARRIS_FILE = os.path.join(BARRIS_DIR, "Barris.shp")
SECTORS_FILE = os.path.join(SECTORS_DIR, "sectors.shp")  

OUTPUT_SECCIONS = os.path.join(data_dir, "seccions_girona_union.geojson")
OUTPUT_BARRIS = os.path.join(data_dir, "barris_girona.geojson")
OUTPUT_SECTORS = os.path.join(data_dir, "sectors_girona.geojson")  # sortida GeoJSON sectors

# =========================
# --- SECCIONS ---
# =========================

seccions = gpd.read_file(SECCIONS_FILE, encoding="utf-8-sig")
print("CRS seccions:", seccions.crs)

# Reprojecta a WGS84
seccions = seccions.to_crs(epsg=4326)

# Dissolve: combina polígons amb el mateix DISTRICTE i SECCIÓ
seccions_union = seccions.dissolve(by=["DISTRICTE", "SECCIÓ"], as_index=False)

# Crear un id únic per cada combinació
seccions_union["id"] = seccions_union.index.astype(int)

# Desa a GeoJSON
seccions_union.to_file(
    OUTPUT_SECCIONS,
    driver="GeoJSON",
    encoding="utf-8"
)
print(f"Seccions processades i guardades a: {OUTPUT_SECCIONS}")

# =========================
# --- BARRIS ---
# =========================

barris = gpd.read_file(BARRIS_FILE, encoding="ISO-8859-1")
print("CRS barris:", barris.crs)

# Reprojecta a WGS84
barris = barris.to_crs(epsg=4326)

# Crear id per cada barri
barris["id"] = barris.index.astype(int)

barris.to_file(
    OUTPUT_BARRIS,
    driver="GeoJSON",
    encoding="utf-8"
)
print(f"Barris processats i guardats a: {OUTPUT_BARRIS}")

# =========================
# --- SECTORS ---
# =========================

# Llegim el shapefile de sectors (shx necessita també .shp al mateix directori)
sectors = gpd.read_file(SECTORS_FILE, encoding="utf-8-sig")
print("CRS sectors:", sectors.crs)

# Reprojecta a WGS84
sectors = sectors.to_crs(epsg=4326)

# Dissolve per alguna columna rellevant, per exemple "SECTOR" (canvia segons el teu shapefile)
if "SECTOR" in sectors.columns:
    sectors_union = sectors.dissolve(by="SECTOR", as_index=False)
else:
    sectors_union = sectors.copy()  # si no hi ha columna, només fem còpia

# Crear id únic
sectors_union["id"] = sectors_union.index.astype(int)

# Desa a GeoJSON
sectors_union.to_file(
    OUTPUT_SECTORS,
    driver="GeoJSON",
    encoding="utf-8"
)
print(f"Sectors processats i guardats a: {OUTPUT_SECTORS}")
