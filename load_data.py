import pandas as pd
import numpy as np
import glob
import os

# 1. Charger et fusionner tous les fichiers PARQUET
path = r'C:\Users\lenovo\Documents\Programming\Python\IA\IDS\CIC-IDS2017' 
all_files = glob.glob(os.path.join(path, "*.parquet"))

df_list = []
for file in all_files:
    print(f"Chargement de {os.path.basename(file)}...")
    # Utilisation de read_parquet au lieu de read_csv
    df_list.append(pd.read_parquet(file, engine='pyarrow'))

# Fusionner en un seul DataFrame
df = pd.concat(df_list, ignore_index=True)

# 2. Nettoyer le nom des colonnes (enlever les espaces inutiles)
df.columns = df.columns.str.strip()

print(f"\nDimensions du dataset complet : {df.shape}")
print("\nRépartition des classes :")
print(df['Label'].value_counts())

print("\n--- Début du nettoyage ---")

# 3. Gérer les valeurs infinies et manquantes
# Le dataset CIC-IDS génère souvent des valeurs infinies (division par zéro lors de la capture)
df.replace([np.inf, -np.inf], np.nan, inplace=True)

# Supprimer les lignes corrompues (recommandé vu la taille du dataset)
df.dropna(inplace=True)
print(f"Dimensions après nettoyage des NaN/Inf : {df.shape}")

# 4. Encodage binaire de la cible
# 0 = Trafic normal (Benign), 1 = Attaque (tout le reste)
df['Label'] = df['Label'].apply(lambda x: 0 if x == 'Benign' else 1)

print("\nNouvelle répartition des classes (0 = Normal, 1 = Attaque) :")
print(df['Label'].value_counts())

# 5. Sauvegarder le résultat final sur le disque dur
output_file = os.path.join(path, "dataset_cleaned.parquet")
print(f"\nSauvegarde en cours vers {output_file}...")
df.to_parquet(output_file, engine='pyarrow')
print("Sauvegarde terminée !")