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
    Prepara el payload JSON con EXACTAMENTE los 6 features del modelo nuevo.
    """
    
    # 1. Recuperar valores
    role_raw = responses.get("Demo_Rol_Trabajo")
    hours_raw = responses.get("Demo_Horas")
    size_raw = responses.get("Demo_Tamano_Org")

    # 2. Validaciones básicas
    if role_raw is None:
        raise ValueError("Error: Falta 'Rol de Trabajo'.")
    if hours_raw is None:
        raise ValueError("Error: Falta 'Horas de uso'.")
    
    # Si falta el tamaño (ej. usuario se saltó algo raro), ponemos 1 por defecto
    if size_raw is None:
        size_raw = 1 

    # 3. Conversión de tipos (CRÍTICO: Int vs Float)
    try:
        role_val = int(role_raw)
        hours_val = int(hours_raw) # <--- ENTERO (Int), NO FLOAT
        size_val = int(size_raw)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Error de tipo de datos. Detalle: {e}")

    # 4. Construcción del diccionario limpio (Solo 6 features)
    features = {
        "Demo_Tamano_Org": size_val,
        "Demo_Rol_Trabajo": role_val,
        "Big5_Apertura": float(scores.get("Big5_Apertura", 0.0)),
        "Demo_Horas": hours_val,  # <--- Confirmado INT
        "Phish_Riesgo_Percibido": float(scores.get("Phish_Riesgo_Percibido", 0.0)),
        "Fatiga_Global_Score": float(scores.get("Fatiga_Global_Score", 0.0))
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