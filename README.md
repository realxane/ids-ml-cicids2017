# ML-IDS : Intrusion Detection System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-orange.svg)](https://scikit-learn.org/)

## Description
Ce projet est un Système de Détection d'Intrusion (IDS) de bout en bout, qui utilise l'apprentissage automatique pour classer le trafic réseau. Entraîné sur le jeu de données de référence **CIC-IDS2017**, le modèle effectue une classification binaire : il distingue le trafic légitime du trafic malveillant (DDoS, force brute, scans de ports, etc.).

L'architecture est scindée en un moteur de prédiction (API) et une interface de supervision en temps réel (Dashboard SOC).

# Architecture du Projet
1. **Ingénierie des Données (`load_data.py`)** : Nettoyage, fusion des fichiers Parquet, et encodage binaire des étiquettes réseau.
2. **Entraînement du Modèle (`train.py`)** : Implémentation d'un algorithme *Random Forest Classifier* avec normalisation des caractéristiques (StandardScaler).
3. **Moteur d'Inférence (`api.py`)** : API REST développée avec **FastAPI** chargeant le modèle sérialisé pour analyser les flux réseau entrants en quelques millisecondes.
4. **Dashboard SOC (`dashboard.py`)** : Interface interactive développée avec **Streamlit** simulant l'interception et l'analyse du trafic en temps réel.

## Résultats

Évaluation sur un jeu de test de 462 762 flux réseau, jamais vus pendant l'entraînement :

| Métrique | Valeur |
| --- | --- |
| Exactitude (accuracy) | 99,89 % |
| Précision (classe Attaque) | 99,58 % |
| Rappel (classe Attaque) | 99,67 % |
| F1-score (classe Attaque) | 99,62 % |
| Taux de faux positifs | 0,07 % |

**Matrice de confusion :**

|  | Prédit Normal | Prédit Attaque |
| --- | --- | --- |
| **Réel Normal** | 395 178 | 286 |
| **Réel Attaque** | 222 | 67 076 |

Le jeu de données est déséquilibré (85,5 % de trafic légitime) : l'exactitude seule est donc trompeuse. Le rappel sur la classe Attaque est la métrique prioritaire, car une attaque non détectée coûte plus cher qu'une fausse alerte. Sur 67 298 attaques, le modèle en a manqué 222 (0,33 %).

## Limites et pistes d'amélioration

- **Classification binaire** : le modèle détecte une attaque sans en identifier le type. Étape suivante : une classification multi-classes (DDoS, force brute, scan, etc.).
- **Généralisation** : CIC-IDS2017 provient d'un réseau de laboratoire. Les performances sur du trafic réel restent à valider, par exemple sur un autre jeu de données comme CSE-CIC-IDS2018.
- **Temps réel simulé** : le tableau de bord rejoue des flux du jeu de données. Une évolution consisterait à capturer le trafic réel (CICFlowMeter, Zeek) et à l'envoyer à l'API.

## Installation & Exécution locale

### Prérequis
- Python 3.11+
- Fichiers `.joblib` du modèle et du scaler générés dans un dossier `export/`

### Installation
```bash
git clone [https://github.com/realxane/ids-ml-cicids2017.git](https://github.com/realxane/ids-ml-cicids2017.git)
cd ids-ml-cicids2017
pip install -r requirements.txt