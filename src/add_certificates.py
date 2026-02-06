"""
merge_energy_last.py

This script merges the Girona rental dataset with the building energy certificates dataset.

- Each rental is linked to a census tract (census_tract_INE), and each certificate 
  corresponds to a census tract (census_tract). The merge uses this key.

- Some census tracts have multiple certificates. For each rental, we take the latest 
  available certificate **up to the year of the rental offer**, to avoid using future information.

- The result is that each rental now has building characteristics (energy rating, CO2 emissions,
  cadastral surface) relevant at the time of the offer, enabling meaningful analysis and modeling.
"""

import os
import pandas as pd

# =========================
# CONFIGURATION PATHS
# =========================
base_dir = os.path.abspath("..")  # assume we are in src/ or similar
data_dir = os.path.join(base_dir, "data")

RENT_CLEAN_CSV = os.path.join(data_dir, "girona_for_rent_combined_clean.csv")
ENERGY_CSV = os.path.join(data_dir, "initial", "girona_energy_certificates.csv")
OUTPUT_CSV = os.path.join(data_dir, "girona_for_rent_with_energy.csv")

# =========================
# LOAD DATASETS
# =========================
print("Loading rental dataset...")
rent = pd.read_csv(RENT_CLEAN_CSV)

print("Loading energy certificates dataset...")
energy = pd.read_csv(ENERGY_CSV)

# =========================
# PREPARE ENERGY DATA
# =========================
if 'data_entrada' in energy.columns:
    energy['data_entrada'] = pd.to_datetime(energy['data_entrada'], errors='coerce')
    energy['year'] = energy['data_entrada'].dt.year
else:
    energy['year'] = None  # fallback if no date column

# Keep only relevant columns
energy_cols = ['census_tract', 'metres_cadastre', 'emissions_de_co2', 'qual_energia', 'year']
energy_sorted = energy[energy_cols].sort_values(['census_tract','year'])

# =========================
# FUNCTION TO GET LAST CERTIFICATE UP TO RENTAL YEAR
# =========================
def get_last_cert(row):
    tract = row['census_tract_INE']
    year_rent = row['year_available']
    
    certs = energy_sorted[(energy_sorted['census_tract'].astype(str) == str(tract)) & 
                          (energy_sorted['year'].notna()) &
                          (energy_sorted['year'] <= year_rent)]
    
    if not certs.empty:
        return certs.iloc[-1][['metres_cadastre','emissions_de_co2','qual_energia']]
    else:
        return pd.Series({'metres_cadastre':None,'emissions_de_co2':None,'qual_energia':None})

# =========================
# APPLY FUNCTION TO RENTALS
# =========================
print("Assigning latest energy certificates up to rental year...")
merged_energy = rent.join(rent.apply(get_last_cert, axis=1))

# =========================
# CHECK RESULTS
# =========================
print("Showing first rows with energy-related columns:")
print(merged_energy[['census_tract_INE','qual_energia','emissions_de_co2','metres_cadastre']].head())

# =========================
# SAVE FINAL DATASET
# =========================
merged_energy.to_csv(OUTPUT_CSV, index=False)
print(f"✔ Dataset with latest energy certificate per rental saved to: {OUTPUT_CSV}")

