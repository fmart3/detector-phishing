import requests
import pandas as pd
import streamlit as st

# =====================================================
# Configuración del endpoint Databricks
# =====================================================

DATABRICKS_ENDPOINT = "api_phishing"

def get_headers():
    """
    Construye headers de autorización usando Streamlit Secrets
    """
    try:
        return {
            "Authorization": f"Bearer {st.secrets['DATABRICKS_TOKEN']}",
            "Content-Type": "application/json"
        }
    except KeyError:
        st.error(
            "❌ Falta DATABRICKS_TOKEN en Streamlit Secrets.\n\n"
            "Configúralo en Settings → Secrets."
        )
        st.stop()


def get_endpoint_url():
    """
    Construye la URL completa del endpoint
    """
    try:
        host = st.secrets["DATABRICKS_HOST"].rstrip("/")
        return f"{host}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations"
    except KeyError:
        st.error(
            "❌ Falta DATABRICKS_HOST en Streamlit Secrets.\n\n"
            "Ejemplo: https://adb-xxxx.azuredatabricks.net"
        )
        st.stop()


# =====================================================
# Predicción
# =====================================================

MODEL_FEATURES = [
    "Fatiga_Global_Score",
    "Big5_Responsabilidad",
    "Big5_Apertura",
    "Demo_Generacion_Edad",
    "Demo_Rol_Trabajo",
    "Demo_Horas",
]

def prepare_features(scores: dict) -> dict:
    """
    Filtra y valida las features que el modelo espera
    """

    missing = [f for f in MODEL_FEATURES if f not in scores]
    if missing:
        raise ValueError(f"❌ Faltan features requeridas por el modelo: {missing}")

    return {
        "Fatiga_Global_Score": float(scores["Fatiga_Global_Score"]),
        "Big5_Responsabilidad": float(scores["Big5_Responsabilidad"]),
        "Big5_Apertura": float(scores["Big5_Apertura"]),
        "Demo_Generacion_Edad": int(scores["Demo_Generacion_Edad"]),
        "Demo_Rol_Trabajo": int(scores["Demo_Rol_Trabajo"]),
        "Demo_Horas": int(scores["Demo_Horas"]),
    }


def predict(features: dict) -> dict:
    """
    Envía features al endpoint de Databricks
    Retorna predicción y probabilidad (si existe)
    """

    url = get_endpoint_url()
    headers = get_headers()

    payload = {
        "dataframe_records": [features]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error("❌ Error al consultar el endpoint de Databricks")
        st.code(response.text)
        st.stop()

    result = response.json()

    # Formato típico Databricks
    prediction = result["predictions"][0]

    return {
        "prediction": int(prediction),
        "raw_response": result
    }
