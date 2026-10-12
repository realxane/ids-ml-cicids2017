import streamlit as st
import requests
import pandas as pd
import random
import time

# Configuration de la page
st.set_page_config(page_title="SOC Dashboard - IDS", page_icon="🛡️", layout="wide")

st.title("🛡️ Dashboard SOC : Détection d'Intrusion ML")
st.markdown("Interface de supervision en temps réel connectée à l'API FastAPI (Random Forest).")

# URL de l'API locale
API_URL = "http://127.0.0.1:8000/predict"

# Initialisation des variables de session pour l'historique
if "history" not in st.session_state:
    st.session_state.history = []
if "analyzed_count" not in st.session_state:
    st.session_state.analyzed_count = 0
if "attack_count" not in st.session_state:
    st.session_state.attack_count = 0

# Chargement mis en cache d'un échantillon du dataset pour la simulation
@st.cache_data
def load_sample_data():
    try:
        # On charge le dataset et on prend 1000 lignes au hasard pour simuler le trafic
        df = pd.read_parquet('CIC-IDS2017/dataset_cleaned.parquet', engine='pyarrow')
        return df.sample(1000)
    except Exception as e:
        st.error(f"Erreur de chargement du dataset: {e}")
        return None

df_sample = load_sample_data()

# Affichage des métriques clés
col1, col2, col3 = st.columns(3)
col1.metric("Flux Analysés", st.session_state.analyzed_count)
col2.metric("Menaces Bloquées", st.session_state.attack_count)
taux = f"{(st.session_state.attack_count / st.session_state.analyzed_count * 100):.1f}%" if st.session_state.analyzed_count > 0 else "0%"
col3.metric("Taux de Menace", taux)

st.divider()

# Bouton d'action pour simuler un nouveau paquet réseau
if st.button("🚀 Intercepter et analyser un nouveau flux réseau", use_container_width=True):
    if df_sample is not None:
        # Prendre une ligne au hasard dans l'échantillon
        row = df_sample.sample(1).iloc[0]
        true_label = row['Label']
        features = row.drop('Label').tolist()

        # Envoi de la requête POST à l'API FastAPI
        try:
            start_time = time.time()
            response = requests.post(API_URL, json={"features": features})
            latency = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                is_attack = result["is_attack"]
                status_text = result["status"]
                
                # Mise à jour des compteurs
                st.session_state.analyzed_count += 1
                if is_attack:
                    st.session_state.attack_count += 1
                    st.error(f"🚨 {status_text} ! (Détecté en {latency:.3f}s)")
                else:
                    st.success(f"✅ {status_text} (Analysé en {latency:.3f}s)")
                
                # Ajout au journal en haut de la liste
                st.session_state.history.insert(0, {
                    "Heure": time.strftime("%H:%M:%S"),
                    "Latence API": f"{latency:.3f}s",
                    "Décision du Modèle": status_text,
                    "Vraie nature (Dataset)": "Attaque" if true_label == 1 else "Normal"
                })
            else:
                st.error(f"Erreur de l'API: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Impossible de se connecter à l'API. Vérifie que FastAPI est lancé dans un autre terminal.")

# Affichage du journal des alertes
st.subheader("📝 Journal des événements réseau")
if st.session_state.history:
    df_history = pd.DataFrame(st.session_state.history)
    st.dataframe(df_history, use_container_width=True)