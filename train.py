import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import time
import os

# 1. Charger les données propres
file_path = r'CIC-IDS2017\dataset_cleaned.parquet'
print("Chargement du dataset nettoyé...")
df = pd.read_parquet(file_path, engine='pyarrow')

# 2. Séparer les caractéristiques (X) et la cible (y)
X = df.drop('Label', axis=1)
y = df['Label']

# 3. Séparation Train/Test (80% / 20%)
# stratify=y garantit que la proportion d'attaques reste la même dans les deux sets
print("Séparation des données en cours...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. Normalisation des données
print("Normalisation des caractéristiques (StandardScaler)...")
scaler = StandardScaler()
# On fit_transform sur le train, et seulement transform sur le test pour éviter la fuite de données
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Entraînement du modèle
# class_weight='balanced' donne plus de poids aux attaques pour contrer le déséquilibre
print("Entraînement du Random Forest (cela peut prendre quelques minutes)...")
start_time = time.time()
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, class_weight='balanced')
rf_model.fit(X_train_scaled, y_train)
print(f"Entraînement terminé en {time.time() - start_time:.2f} secondes.")

# 6. Évaluation
print("\n--- Évaluation sur les données de test ---")
y_pred = rf_model.predict(X_test_scaled)

print("\nMatrice de confusion :")
# Ligne 1 : Vrais Négatifs (Normal bloqué à juste titre), Faux Positifs (Normal bloqué à tort)
# Ligne 2 : Faux Négatifs (Attaque non détectée), Vrais Positifs (Attaque bien détectée)
print(confusion_matrix(y_test, y_pred))

print("\nRapport de classification :")
print(classification_report(y_test, y_pred, target_names=['Trafic Normal (0)', 'Attaque (1)', ]))


import joblib
import os


print("\n--- Sauvegarde pour la mise en production ---")
# Création d'un sous-dossier 'export' pour garder ton espace de travail propre
export_dir = 'export'
os.makedirs(export_dir, exist_ok=True)

model_path = os.path.join(export_dir, 'ids_random_forest.joblib')
scaler_path = os.path.join(export_dir, 'ids_scaler.joblib')

print("Exportation du modèle et du scaler en cours...")
# Sérialisation des objets
joblib.dump(rf_model, model_path)
joblib.dump(scaler, scaler_path)

print(f"✅ Modèle sauvegardé : {model_path}")
print(f"✅ Scaler sauvegardé : {scaler_path}")
print("Le moteur de détection est prêt à être embarqué dans une API !")