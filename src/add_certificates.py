import os
import pandas as pd

# CONFIGURACIÓ PATHS
base_dir = os.path.abspath("..")  # assumeix que estem a src/ o similar
data_dir = os.path.join(base_dir, "data")

RENT_CLEAN_CSV = os.path.join(data_dir, "girona_for_rent_combined_clean.csv")
ENERGY_CSV = os.path.join(data_dir, "initial", "girona_energy_certificates.csv")
OUTPUT_CSV = os.path.join(data_dir, "girona_for_rent_with_energy.csv")

# Carrega datasets
print("Carregant dataset de lloguers...")
rent = pd.read_csv(RENT_CLEAN_CSV)

print("Carregant certificats energètics...")
energy = pd.read_csv(ENERGY_CSV)

# Agafa només l’últim certificat per cada census_tract
if 'data_entrada' in energy.columns:
    energy['data_entrada'] = pd.to_datetime(energy['data_entrada'], errors='coerce')
    energy_sorted = energy.sort_values(['census_tract','data_entrada'])
else:
    energy_sorted = energy.sort_values('census_tract')

energy_last = energy_sorted.groupby('census_tract').last().reset_index()

# Merge amb dataset de lloguers
cols_to_merge = ['census_tract', 'metres_cadastre', 'emissions_de_co2', 'qual_energia']

merged = rent.merge(
    energy_last[cols_to_merge],
    left_on='census_tract_INE',
    right_on='census_tract',
    how='left'
)

# Comprovació ràpida
print("Mostrant primeres files amb columnes d’interès:")
print(merged[['census_tract_INE','qual_energia','emissions_de_co2','metres_cadastre']].head())

# Desa dataset final
merged.to_csv(OUTPUT_CSV, index=False)
print(f"✔ Dataset amb últim certificat energètic desat a: {OUTPUT_CSV}")
