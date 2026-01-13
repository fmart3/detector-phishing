import requests
import streamlit as st

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "phishing-endpoint"

MODEL_FEATURES = [
    "Fatiga_Global_Score",
    "Phish_Susceptibilidad",
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

def prepare_features(scores: dict) -> dict:
    missing = [f for f in MODEL_FEATURES if f not in scores]
    if missing:
        raise ValueError(f"❌ Faltan features: {missing}")

    return {
        "Fatiga_Global_Score": float(scores["Fatiga_Global_Score"]),
        "Phish_Susceptibilidad": float(scores["Phish_Susceptibilidad"]),
        "Big5_Apertura": float(scores["Big5_Apertura"]),
        "Phish_Riesgo_Percibido": float(scores["Phish_Riesgo_Percibido"]),
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

    payload = {
        "dataframe_records": [features]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error("❌ Error al invocar endpoint Databricks")
        st.code(response.text)
        st.stop()

    result = response.json()
    prediction_row = result["predictions"][0]

    # Caso 1: modelo PyFunc devuelve dict con keys
    if isinstance(prediction_row, dict):
        if "prediction" in prediction_row:
            pred_class = int(prediction_row["prediction"])
            probability = float(prediction_row.get("probability"))
        else:
            # fallback genérico (por índice)
            pred_class = int(list(prediction_row.values())[0])
            probability = None

    # Caso 2: modelo clásico (lista de números)
    else:
        pred_class = int(prediction_row)
        probability = None


    return {
        "prediction": pred_class,
        "probability": probability,
        #"raw_response": result
    }
