import requests
import streamlit as st

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "api-phishing"

MODEL_FEATURES = [
    "Fatiga_Global_Score",
    "Big5_Responsabilidad",
    "Big5_Apertura",
    "Phish_Riesgo_Percibido",
    "Demo_Rol_Trabajo",
    "Demo_Horas"
]

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
    """
    Intenta obtener el host desde distintos nombres comunes
    """
    possible_keys = [
        "DATABRICKS_HOST",
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_INSTANCE"
    ]

    for key in possible_keys:
        if key in st.secrets:
            host = st.secrets[key].rstrip("/")
            if not host.startswith("http"):
                st.error(f"❌ {key} debe comenzar con https://")
                st.stop()
            return host

    st.error(
        "❌ No se encontró el HOST de Databricks.\n\n"
        "Configura uno de los siguientes en Streamlit Secrets:\n"
        "- DATABRICKS_HOST\n"
        "- DATABRICKS_WORKSPACE_URL\n"
        "- DATABRICKS_INSTANCE\n\n"
        "Ejemplo:\n"
        "https://adb-123456789012.3.azuredatabricks.net"
    )
    st.stop()


def get_endpoint_url():
    host = get_databricks_host()
    return f"{host}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations"


# =====================================================
# Features
# =====================================================

def prepare_features(scores: dict) -> dict:
    missing = [f for f in MODEL_FEATURES if f not in scores]
    if missing:
        raise ValueError(f"❌ Faltan features requeridas por el modelo: {missing}")

    return {
        "Fatiga_Global_Score": float(scores["Fatiga_Global_Score"]),
        "Big5_Responsabilidad": float(scores["Big5_Responsabilidad"]),
        "Big5_Apertura": float(scores["Big5_Apertura"]),
        "Phish_Riesgo_Percibido": int(scores["Phish_Riesgo_Percibido"]),
        "Demo_Rol_Trabajo": int(scores["Demo_Rol_Trabajo"]),
        "Demo_Horas": int(scores["Demo_Horas"]),
    }


# =====================================================
# Predicción
# =====================================================

def predict(scores: dict) -> dict:
    url = get_endpoint_url()
    headers = get_headers()
    features = prepare_features(scores)

    payload = {"dataframe_records": [features]}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error("❌ Error al invocar endpoint Databricks")
        st.code(response.text)
        st.stop()

    result = response.json()

    prediction = int(result["predictions"][0])

    probability = None
    if "probabilities" in result:
        probability = float(result["probabilities"][0][1])

    return {
        "prediction": prediction,
        "probability": probability,
        "raw_response": result
    }

