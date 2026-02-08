import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# =========================
# CONFIGURATION PATHS
# =========================
base_dir = os.path.abspath("..")
data_dir = os.path.join(base_dir, "data")

INPUT_CSV = os.path.join(data_dir, "final_final_dataset.csv")
OUTPUT_PCA_SCORES = os.path.join(data_dir, "results", "pca_scores_sector.csv")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_CSV)

# =========================
# VARIABLES TO USE (same as first PCA)
# =========================
pca_cols = [
    "renda_med", "renda_mediana", "gini", "p80_p20",
    "pct_65_plus", "pct_under18", "pct_single_household"
]

# Aggregate per sector_oficial
df_sector = df.groupby("sector_oficial")[pca_cols].mean()

# =========================
# STANDARDIZE
# =========================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_sector)

# =========================
# PCA
# =========================
pca = PCA(n_components=2)
pca_scores = pca.fit_transform(X_scaled)

# =========================
# CREATE SCORES DATAFRAME
# =========================
scores_df = pd.DataFrame(
    pca_scores, 
    columns=["PCA1", "PCA2"], 
    index=df_sector.index
).reset_index().rename(columns={"sector_oficial": "sector"})

# Variància explicada
print("Explained variance ratio per component:")
print(pca.explained_variance_ratio_)

# Variància acumulada
print("Explained variance acumulada per les 2 components:")
print(pca.explained_variance_ratio_.sum())

# =========================
# SAVE TO CSV
# =========================
scores_df.to_csv(OUTPUT_PCA_SCORES, index=False)
print(f"✔ PCA scores exported to: {OUTPUT_PCA_SCORES}")
