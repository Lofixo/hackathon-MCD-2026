import os
import pandas as pd

# =========================
# CONFIGURACIÓ PATHS
# =========================
base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

INPUT_CSV = os.path.join(data_dir, "girona_for_rent_combined_clean.csv")
OUTPUT_CSV = os.path.join(data_dir, "girona_rent_leaflet_view.csv")

# =========================
# 1. Carrega dataset clean
# =========================
df = pd.read_csv(INPUT_CSV)

# =========================
# 2. Feature bàsica per visualització
# =========================
df["price_per_m2"] = df["price"] / df["area"]

# =========================
# 3. Selecciona només camps necessaris
# =========================
leaflet_view = df[
    [
        "lat",
        "lon",
        "barri_oficial",
        "price",
        "area",
        "price_per_m2",
        "year_available"
    ]
].dropna()

# =========================
# 4. Desa CSV
# =========================
leaflet_view.to_csv(OUTPUT_CSV, index=False)

print("✔ Dataset Leaflet creat correctament")
print(f"Files: {leaflet_view.shape[0]}")
print(f"Fitxer: {OUTPUT_CSV}")
