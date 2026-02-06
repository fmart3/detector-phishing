import os
import joblib
import pandas as pd
import numpy as np

# Ruta al modelo local
MODEL_PATH = "phishing_model.pkl"

# Variable global para mantener el modelo en memoria
_loaded_model = None

def load_local_model():
    """Carga el modelo .pkl en memoria si no está cargado."""
    global _loaded_model
    if _loaded_model is not None:
        return _loaded_model
    
    if os.path.exists(MODEL_PATH):
        try:
            print(f"📂 Cargando modelo local desde: {MODEL_PATH} ...")
            _loaded_model = joblib.load(MODEL_PATH)
            print("✅ Modelo cargado exitosamente.")
        except Exception as e:
            print(f"❌ Error al cargar {MODEL_PATH}: {e}")
    else:
        print(f"⚠️ Advertencia: No se encontró el archivo {MODEL_PATH} en la raíz.")
    
    return _loaded_model

def prepare_features(scores: dict, responses: dict):
    """
    Convierte las respuestas y scores en un DataFrame de Pandas.
    IMPORTANTE: El orden y nombre de columnas debe ser IDÉNTICO al entrenamiento.
    """
    try:
        # Extraemos los valores convirtiéndolos al tipo correcto
        # Estos nombres de columnas deben coincidir con tu X_train del notebook
        data = {
            # "Demo_Rol_Trabajo": [int(responses.get("Demo_Rol_Trabajo", 0))],
            # "Fatiga_Global_Score": [float(scores.get("Fatiga_Global_Score", 0.0))],
            # "Big5_Apertura": [float(scores.get("Big5_Apertura", 0.0))],
            # "Phish_Riesgo_Percibido": [float(scores.get("Phish_Riesgo_Percibido", 0.0))],
            # "Phish_Autoeficacia": [float(scores.get("Phish_Autoeficacia", 0.0))],
            # "Phish_Susceptibilidad": [float(scores.get("Phish_Susceptibilidad", 0.0))]
            "Demo_Tamano_Org": [int(responses.get("Demo_Tamano_Org", 0))],
            "Demo_Rol_Trabajo": [int(responses.get("Demo_Rol_Trabajo", 0))],
            "Big5_Apertura": [float(scores.get("Big5_Apertura", 0.0))],
            "Demo_Horas": [int(responses.get("Demo_Horas", 0))],
            "Phish_Riesgo_Percibido": [float(scores.get("Phish_Riesgo_Percibido", 0.0))],
            "Fatiga_Global_Score": [float(scores.get("Fatiga_Global_Score", 0.0))],
        }
        
        # Creamos DataFrame (formato que espera el Pipeline de Sklearn)
        df_features = pd.DataFrame(data)
        return df_features

    except Exception as e:
        print(f"❌ Error preparando features: {e}")
        return None

def predict_model(features_df):
    """
    Recibe un DataFrame, lo pasa por el modelo local y devuelve la probabilidad.
    """
    model = load_local_model()
    
    if model is None:
        return {"probability": 0.0, "risk_level": "Error: Modelo no cargado"}
    
    if features_df is None:
         return {"probability": 0.0, "risk_level": "Error: Datos inválidos"}

    try:
        # El modelo (pipeline) ya incluye el scaler, así que pasamos el DF directo.
        # predict_proba devuelve array: [[prob_clase_0, prob_clase_1]]
        prediction_probs = model.predict_proba(features_df)
        
        # Obtenemos la probabilidad de la clase 1 (Susceptible/Phishing)
        prob_phishing = float(prediction_probs[0][1])
        
        # Regla de Negocio para el Nivel de Riesgo
        risk = "ALTO" if prob_phishing > 0.7 else "MEDIO" if prob_phishing > 0.4 else "BAJO"
        
        return {
            "probability": prob_phishing,
            "risk_level": risk,
            "source": "local_model_pkl" # Para saber que vino del archivo local
        }

    except Exception as e:
        print(f"❌ Error en predicción local: {e}")
        return {"probability": 0.0, "risk_level": "Error Predicción"}