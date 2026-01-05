import requests
import streamlit as st

DATABRICKS_ENDPOINT = "api_phishing"

MODEL_FEATURES = [
    "Fatiga_Global_Score",
    "Big5_Responsabilidad",
    "Big5_Apertura",
    "Demo_Generacion_Edad",
    "Demo_Rol_Trabajo",
    "Demo_Horas",
]


def get_headers():
    try:
        return {
            "Authorization": f"Bearer {st.secrets['DATABRICKS_TOKEN']}",
            "Content-Type": "application/json"
        }
    except KeyError:
        st.error("❌ Falta DATABRICKS_TOKEN en Streamlit Secrets")
        st.stop()


def get_endpoint_url():
    try:
        host = st.secrets["DATABRICKS_HOST"].rstrip("/")
        return f"{host}/serving-endpoints/{DATABRICKS_ENDPOINT}/invocations"
    except KeyError:
        st.error("❌ Falta DATABRICKS_HOST en Streamlit Secrets")
        st.stop()


def prepare_features(scores: dict) -> dict:
    missing = [f for f in MODEL_FEATURES if f not in scores]
    if missing:
        raise ValueError(f"❌ Faltan features requeridas por el modelo: {missing}")

    return {k: scores[k] for k in MODEL_FEATURES}


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

    return {
        "prediction": int(result["predictions"][0]),
        "raw": result
    }
