# /utils/databricks.py

import requests
import streamlit as st

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "phishing-endpoint"

# =====================================================
# Helpers
# =====================================================

def get_headers():
    if "DATABRICKS_TOKEN" not in st.secrets:
        st.error("❌ Falta DATABRICKS_TOKEN en Streamlit Secrets")
        st.stop()

    return {
        "Authorization": f"Bearer {st.secrets['DATABRICKS_TOKEN']}",
        "Content-Type": "application/json"
    }

def get_databricks_host():
    for key in [
        "DATABRICKS_HOST",
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_INSTANCE"
    ]:
        if key in st.secrets:
            host = st.secrets[key].rstrip("/")
            if not host.startswith("http"):
                st.error(f"❌ {key} debe comenzar con https://")
                st.stop()
            return host

    st.error("❌ No se encontró el HOST de Databricks")
    st.stop()

def get_endpoint_url():
    return f"{get_databricks_host()}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations"

# =====================================================
# Features
# =====================================================

def prepare_features(scores: dict, responses: dict) -> dict:
    """
    Prepara el payload JSON.
    NOTA: Envía TODAS las variables para satisfacer el esquema del modelo antiguo
    hasta que el endpoint se actualice a la versión de solo 6 variables.
    """
    
    # 1. Recuperar valores clave y validar
    role_raw = responses.get("Demo_Rol_Trabajo")
    hours_raw = responses.get("Demo_Horas")
    size_raw = responses.get("Demo_Tamano_Org")

    if role_raw is None: role_raw = 1
    if hours_raw is None: hours_raw = 1
    if size_raw is None: size_raw = 1

    # 2. Construcción del diccionario (Mapeo completo)
    features = {
        # --- Las 6 Variables del Modelo Nuevo (Prioridad) ---
        "Demo_Tamano_Org": int(size_raw),
        "Demo_Rol_Trabajo": int(role_raw),
        "Big5_Apertura": float(scores.get("Big5_Apertura", 0.0)),
        "Demo_Horas": int(hours_raw),
        "Phish_Riesgo_Percibido": float(scores.get("Phish_Riesgo_Percibido", 0.0)),
        "Fatiga_Global_Score": float(scores.get("Fatiga_Global_Score", 0.0)),

        # --- Variables Extras (Requeridas por el Modelo Antiguo) ---
        # Demográficos (Integers / Longs)
        "Demo_Pais": int(responses.get("Demo_Pais", 1)),
        "Demo_Tipo_Organizacion": int(responses.get("Demo_Tipo_Organizacion", 1)),
        "Demo_Industria": int(responses.get("Demo_Industria", 1)),
        "Demo_Genero": int(responses.get("Demo_Genero", 1)),
        "Demo_Generacion_Edad": int(responses.get("Demo_Generacion_Edad", 1)),
        "Demo_Nivel_Educacion": int(responses.get("Demo_Nivel_Educacion", 1)),

        # Scores Psicológicos (Doubles / Floats)
        "Phish_Susceptibilidad": float(scores.get("Phish_Susceptibilidad", 0.0)),
        "Phish_Autoeficacia": float(scores.get("Phish_Autoeficacia", 0.0)),
        "Phish_Awareness": float(scores.get("Phish_Awareness", 0.0))
    }

    return features

# =====================================================
# Predicción
# =====================================================

def predict(features: dict) -> dict:
    url = get_endpoint_url()
    headers = get_headers()

    # Formato 'dataframe_records'
    payload = {
        "dataframe_records": [features]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión con Databricks: {e}")
        st.stop()

    if response.status_code != 200:
        st.error(f"❌ Error del Modelo (Status {response.status_code})")
        # Si ves un error aquí de 'missing inputs', es que Databricks 
        # no ha actualizado el endpoint a la versión nueva.
        st.code(response.text)
        st.stop()

    result = response.json()
    
    if "predictions" in result:
        prediction_row = result["predictions"][0]

        if isinstance(prediction_row, dict):
            pred_class = int(prediction_row.get("prediction", 0))
            probability = prediction_row.get("probability") 
            if probability is not None:
                probability = float(probability)
        else:
            pred_class = int(prediction_row)
            probability = None
    else:
        st.error("Formato de respuesta desconocido")
        st.write(result)
        st.stop()

    return {
        "prediction": pred_class,
        "probability": probability
    }