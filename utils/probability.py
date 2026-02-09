import os
import joblib
import pandas as pd
import numpy as np

# Ruta al modelo local (Asegúrate de que el .pkl esté en la carpeta raíz)
MODEL_PATH = "phishing_model.pkl"

# Variable global para mantener el modelo en memoria (caché)
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
            _loaded_model = None
    else:
        print(f"⚠️ Advertencia: No se encontró el archivo {MODEL_PATH} en la raíz.")
    
    return _loaded_model

def prepare_features(scores: dict, responses: dict):
    """
    Convierte las respuestas y scores en un DataFrame de Pandas.
    IMPORTANTE: El orden de estas columnas debe ser IDÉNTICO al que usaste
    en tu X_train cuando entrenaste el modelo.
    """
    try:
        # Mapeo de datos para el modelo
        data = {
            "Demo_Tamano_Org": [int(responses.get("Demo_Tamano_Org", 0))],
            "Demo_Rol_Trabajo": [int(responses.get("Demo_Rol_Trabajo", 0))],
            "Big5_Apertura": [float(scores.get("Big5_Apertura", 0.0))],
            "Demo_Horas": [int(responses.get("Demo_Horas", 0))],
            "Phish_Riesgo_Percibido": [float(scores.get("Phish_Riesgo_Percibido", 0.0))],
            "Fatiga_Global_Score": [float(scores.get("Fatiga_Global_Score", 0.0))],
        }
        
        # Creamos DataFrame
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
        print("❌ Error: Intentando predecir sin modelo cargado.")
        return {"probability": 0.0, "risk_level": "Error: Modelo no cargado"}
    
    if features_df is None:
         return {"probability": 0.0, "risk_level": "Error: Datos inválidos"}

    try:
        # predict_proba devuelve array: [[prob_clase_0, prob_clase_1]]
        # Asumimos que la clase 1 es la "Vulnerable/Phishing"
        prediction_probs = model.predict_proba(features_df)
        prob_phishing = float(prediction_probs[0][1])
        
        # Regla de Negocio para el Nivel de Riesgo
        if prob_phishing > 0.7:
            risk = "ALTO"
        elif prob_phishing > 0.4:
            risk = "MEDIO"
        else:
            risk = "BAJO"
        
        return {
            "probability": prob_phishing,
            "risk_level": risk,
            "source": "local_model_pkl"
        }

    except Exception as e:
        print(f"❌ Error en predicción local: {e}")
        return {"probability": 0.0, "risk_level": "Error Predicción"}