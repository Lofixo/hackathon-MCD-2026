"""
merge_sociodemographic.py

Merge Girona rental dataset (with energy & services) with key sociodemographic features.

- Only the most relevant sociodemographic variables are included.
- For multiple years per census tract, the latest available before the rental year is used.
"""

import os
import pandas as pd

# =========================
# PATH CONFIG
# =========================
base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

# Dataset de lloguers ja amb energia i serveis
RENT_CSV = os.path.join(data_dir, "interim", "girona_for_rent_with_services_binary.csv")
SOCIO_CSV = os.path.join(data_dir, "initial", "girona_sociodemographic.csv")
OUTPUT_CSV = os.path.join(data_dir, "girona_for_rent_final.csv")

# =========================
# LOAD DATA
# =========================
rent = pd.read_csv(RENT_CSV)
socio = pd.read_csv(SOCIO_CSV)

# =========================
# NORMALIZE CODES
# =========================
rent['census_tract_INE'] = rent['census_tract_INE'].astype(str)
socio['census_tract'] = socio['census_tract'].astype(str)

# =========================
# PARSE YEAR (if exists)
# =========================
if 'year' in socio.columns:
    socio['year'] = socio['year'].astype(int)
elif 'data' in socio.columns:
    socio['year'] = pd.to_datetime(socio['data'], errors='coerce').dt.year
else:
    socio['year'] = 9999  # fallback

socio_sorted = socio.sort_values(['census_tract','year'])

# =========================
# FUNCTION: get last available before rental year
# =========================
def get_last_socio(tract, rental_year):
    df = socio_sorted[socio_sorted['census_tract'] == tract]
    df = df[df['year'] <= rental_year]
    if df.empty:
        return pd.Series()
    return df.iloc[-1]

# =========================
# APPLY FUNCTION
# =========================
socio_features = rent.apply(
    lambda row: get_last_socio(row['census_tract_INE'], row['year_available']),
    axis=1
)

# =========================
# KEEP ONLY RELEVANT COLUMNS AND RENAME
# =========================
relevant_cols = {
    'media_de_la_renta_por_unidad_de_consumo': 'renda_med',
    'mediana_de_la_renta_por_unidad_de_consumo': 'renda_mediana',
    'indice_de_gini': 'gini',
    'distribucion_de_la_renta_p80_p20': 'p80_p20',
    'porcentaje_de_poblacion_de_65_y_mas_anos': 'pct_65_plus',
    'porcentaje_de_poblacion_menor_de_18_anos': 'pct_under18',
    'porcentaje_de_hogares_unipersonales': 'pct_single_household'
}

socio_features = socio_features[list(relevant_cols.keys())].rename(columns=relevant_cols)

# =========================
# MERGE FINAL
# =========================
rent_final = pd.concat([rent, socio_features.reset_index(drop=True)], axis=1)

# =========================
# SAVE
# =========================
rent_final.to_csv(OUTPUT_CSV, index=False)
print(f"✔ Final dataset with sociodemographic features saved to: {OUTPUT_CSV}")
