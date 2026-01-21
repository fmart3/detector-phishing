# /utils/databricks.py

import requests
import pandas as pd
import streamlit as st

# =====================================================
# Configuración
# =====================================================

# Asegúrate de que este nombre coincida con tu Endpoint en Databricks
DATABRICKS_ENDPOINT = "phishing-endpoint" 

def get_config():
    """Recupera configuración sin usar st.stop() para no romper hilos"""
    try:
        token = st.secrets["DATABRICKS_TOKEN"]
        
        # Lógica para obtener el host
        host = None
        for key in ["DATABRICKS_HOST", "DATABRICKS_WORKSPACE_URL", "DATABRICKS_INSTANCE"]:
            if key in st.secrets:
                host = st.secrets[key].rstrip("/")
                break
        
        if not host or not token:
            raise ValueError("Faltan credenciales en secrets.toml")
            
        return token, host
    except Exception as e:
        print(f"⚠️ Error de configuración: {e}")
        return None, None

def get_endpoint_url(host):
    return f"{host}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations"

# =====================================================
# Features (SOLO LAS 6 NECESARIAS)
# =====================================================

def prepare_features(scores: dict, responses: dict):
    """
    Crea un DataFrame exacto con las 6 columnas que el modelo LITE espera.
    """
    
    # 1. Recuperar valores (con valores por defecto seguros)
    # Convertimos a int/float explícitamente para asegurar tipos
    try:
        data = {
            "Demo_Rol_Trabajo": [int(responses.get("Demo_Rol_Trabajo", 1))],
            "Demo_Horas": [int(responses.get("Demo_Horas", 1))],
            "Demo_Tamano_Org": [int(responses.get("Demo_Tamano_Org", 1))],
            
            "Fatiga_Global_Score": [float(scores.get("Fatiga_Global_Score", 0.0))],
            "Big5_Apertura": [float(scores.get("Big5_Apertura", 0.0))],
            "Phish_Riesgo_Percibido": [float(scores.get("Phish_Riesgo_Percibido", 0.0))]
        }
    except Exception as e:
        # Si algo falla en la conversión, lanzamos error para verlo en logs
        raise ValueError(f"Error procesando tipos de datos: {e}")

    # 2. Crear DataFrame
    df = pd.DataFrame(data)
    
    # Ordenamos columnas alfabéticamente o según lista fija si es necesario.
    # Con dataframe_split, el orden se envía explícitamente, así que es seguro.
    return df

# =====================================================
# Predicción
# =====================================================

def predict(feature_df):
    """
    Envía el DataFrame al endpoint.
    Retorna un diccionario seguro siempre, incluso si falla.
    """
    token, host = get_config()
    
    if not token or not host:
        return {"prediction": 0, "probability": 0.0}

    url = get_endpoint_url(host)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Usamos 'split' porque es el estándar nativo de MLflow/Pandas
    # Genera: { "columns": ["A", "B"], "data": [[1, 2]] }
    payload = {
        "dataframe_split": feature_df.to_dict(orient="split")
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        # Si la respuesta no es exitosa, imprimimos el error pero no matamos la app
        if response.status_code != 200:
            print(f"❌ Error API Databricks ({response.status_code}): {response.text}")
            return {"prediction": 0, "probability": 0.0}

        result = response.json()
        
        # Parseo robusto de la respuesta
        # Databricks puede devolver listas o dicts dependiendo de la versión
        predictions = result.get("predictions", [])
        
        if len(predictions) > 0:
            first_pred = predictions[0]
            
            # Caso 1: Devuelve objeto completo {'prediction': 1, 'probability': 0.8}
            if isinstance(first_pred, dict):
                return {
                    "prediction": int(first_pred.get("prediction", 0)),
                    "probability": float(first_pred.get("probability", 0.0))
                }
            # Caso 2: Devuelve solo el valor [0] o [1] (Modelos viejos)
            else:
                return {"prediction": int(first_pred), "probability": 0.0}
                
        return {"prediction": 0, "probability": 0.0}

    except Exception as e:
        print(f"❌ Excepción conectando a Databricks: {e}")
        # Retorno seguro (Falso negativo es mejor que crash)
        return {"prediction": 0, "probability": 0.0}