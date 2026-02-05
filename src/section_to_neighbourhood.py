import geopandas as gpd
import os

# =========================
# CONFIGURACIÓ DE PATHS
# =========================

base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

SECCIONS_SHP = os.path.join(data_dir, "seccions_girona", "Seccions.shp")
BARRIS_DBF = os.path.join(data_dir, "barris_girona", "Barris.dbf")
OUTPUT_CSV = os.path.join(data_dir, "section_to_neighbourhood_clean.csv")
OUTPUT_GPKG = os.path.join(data_dir, "section_to_neighbourhood_clean.gpkg")  # amb geometria

# =========================
# 1. Carrega les dades
# =========================

seccions = gpd.read_file(SECCIONS_SHP)
barris = gpd.read_file(BARRIS_DBF)

# =========================
# 2. Assegura CRS coherent
# =========================

seccions = seccions.to_crs(barris.crs)

# =========================
# 3. Calcula intersecció de geometries
# =========================

interseccions = gpd.overlay(seccions, barris, how='intersection', keep_geom_type=False)

# =========================
# 4. Conserva només polígons i multipolígons
# =========================

interseccions = interseccions[interseccions.geometry.type.isin(['Polygon','MultiPolygon'])]

# =========================
# 5. Calcula l'àrea de cada intersecció
# =========================

interseccions['AREA_INTERSECCIO'] = interseccions.geometry.area

# =========================
# 6. Assigna a cada secció el barri amb major àrea d'intersecció
# =========================

idx = interseccions.groupby(['SECCIÓ', 'DISTRICTE'])['AREA_INTERSECCIO'].idxmax()
seccions_unics = interseccions.loc[idx]

# =========================
# 7. Crea codis normalitzats i identificadors oficials
# =========================

seccions_unics['district_id'] = seccions_unics['DISTRICTE'].astype(int).astype(str).str.zfill(2)
seccions_unics['section_id'] = seccions_unics['SECCIÓ'].astype(int).astype(str).str.zfill(3)

seccions_unics['census_tract_INE'] = '17907' + seccions_unics['district_id'] + seccions_unics['section_id']
seccions_unics['census_tract_IDESCAT'] = '179072' + seccions_unics['district_id'] + seccions_unics['section_id']

# =========================
# 8. Selecciona les columnes finals
# =========================

cols = ['DISTRICTE', 'SECCIÓ', 'district_id', 'section_id',
        'census_tract_INE', 'census_tract_IDESCAT', 'BARRIS', 'geometry']

seccions_unics = seccions_unics[cols]

# =========================
# 9. Ordena per districte i secció
# =========================

seccions_unics = seccions_unics.sort_values(by=['DISTRICTE','SECCIÓ'])

# =========================
# 10. Guarda CSV i GeoPackage amb geometria
# =========================

# CSV sense geometria (només codis i barri)
seccions_unics.drop(columns='geometry').to_csv(OUTPUT_CSV, index=False)

# GeoPackage amb geometria
seccions_unics.to_file(OUTPUT_GPKG, layer='section_to_neighbourhood', driver='GPKG')

print("✔ Assignació única, neta i ordenada completada!")
print(f"CSV creat: {OUTPUT_CSV}")
print(f"GeoPackage creat amb geometria: {OUTPUT_GPKG}")
