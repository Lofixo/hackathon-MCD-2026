import os
import pandas as pd
from assign_section import assign_district 

# =========================
# CONFIGURACIÓ DE PATHS
# =========================
base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

REAL_CSV = os.path.join(data_dir, "initial", "girona_for_rent.csv")
SYNTHETIC_CSV = os.path.join(data_dir, "initial", "girona_for_rent_synthetic.csv")
OUTPUT_CSV = os.path.join(data_dir, "interim", "girona_for_rent_combined_clean.csv")

# =========================
# 1. Carrega datasets
# =========================
real = pd.read_csv(REAL_CSV)
synthetic = pd.read_csv(SYNTHETIC_CSV)

# Afegim any disponible si no existeix
if 'year_available' not in real.columns:
    real['year_available'] = 2026

# Reindex per assegurar columnes compatibles
all_cols = list(set(real.columns) | set(synthetic.columns))
real = real.reindex(columns=all_cols)
synthetic = synthetic.reindex(columns=all_cols)

# Concatenem
rent_all = pd.concat([real, synthetic], ignore_index=True)
print("Total files combinades:", rent_all.shape[0])

# =========================
# 2. Assignar secció i barri a cada fila
# =========================
district_info = rent_all.apply(
    lambda row: assign_district(row['lat'], row['lon']),
    axis=1
)

# Convertim en DataFrame i concatenem
district_df = pd.DataFrame(list(district_info))
rent_all = pd.concat([rent_all, district_df], axis=1)

# =========================
# 3. Eliminar files sense assignació
# =========================
rent_all_clean = rent_all.dropna(subset=['districte', 'section', 'census_tract_INE'])
print("Files després de netejar:", rent_all_clean.shape[0])

# =========================
# 4. Desa el dataset final
# =========================
rent_all_clean.to_csv(OUTPUT_CSV, index=False)
print(f"Dataset final creat: {OUTPUT_CSV}")
