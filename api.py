from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

# Initialisation de l'application FastAPI
app = FastAPI(title="API de Détection d'Intrusion (IDS)", description="API pour classifier le trafic réseau (Normal ou Attaque)")

# Variables globales pour le modèle et le scaler
rf_model = None
scaler = None

# Modèle de données attendu pour la requête POST
# On attend une liste de 77 valeurs numériques représentant les caractéristiques du flux réseau
class NetworkFlow(BaseModel):
    features: list[float]

@app.on_event("startup")
def load_model():
    """Charge le modèle et le scaler en mémoire au démarrage de l'API."""
    global rf_model, scaler
    try:
        rf_model = joblib.load('export/ids_random_forest.joblib')
        scaler = joblib.load('export/ids_scaler.joblib')
        print("Modèle et Scaler chargés avec succès.")
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")

@app.get("/")
def home():
    return {"message": "L'API de détection d'intrusion est opérationnelle. Accédez à /docs pour tester."}

@app.post("/predict")
def predict_intrusion(flow: NetworkFlow):
    """Reçoit les données réseau, les normalise et prédit s'il s'agit d'une attaque."""
    if len(flow.features) != 77:
        raise HTTPException(status_code=400, detail=f"Le modèle attend 77 caractéristiques, mais {len(flow.features)} ont été fournies.")
    
    # 1. Conversion de la liste en tableau NumPy 2D (1 ligne, 77 colonnes)
    trame_reseau_brute = np.array([flow.features])
    
    # 2. Mise à l'échelle (Standardization)
    trame_scaled = scaler.transform(trame_reseau_brute)
    
    # 3. Prédiction
    verdict = rf_model.predict(trame_scaled)
    
    # 4. Formatage de la réponse
    is_attack = bool(verdict[0] == 1)
    status = "ALERTE INTRUSION" if is_attack else "Trafic légitime"
    
    return {
        "status": status,
        "is_attack": is_attack
    }