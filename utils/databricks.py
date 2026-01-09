import requests
import streamlit as st

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "phishing-endpoint"

def get_model_features():
    url = f"{get_databricks_host()}/api/2.0/serving-endpoints/{DATABRICKS_ENDPOINT}"
    headers = get_headers()

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(
            f"❌ Error al obtener metadata del endpoint Databricks: {response.text}"
        )

    data = response.json()

    # Validación defensiva
    if "config" not in data or "served_models" not in data["config"]:
        raise RuntimeError(
            "❌ El endpoint no contiene 'served_models'. "
            "Verifica que el endpoint esté activo y tenga un modelo servido."
        )

    served_models = data["config"]["served_models"]

    if not served_models:
        raise RuntimeError("❌ No hay modelos servidos en este endpoint.")

    served_model = served_models[0]

    signature = served_model.get("signature")
    if not signature or "inputs" not in signature:
        raise RuntimeError("❌ El modelo no tiene signature definida en MLflow.")

    # MLflow guarda inputs como string JSON
    import json
    inputs = json.loads(signature["inputs"])

    feature_names = [f["name"] for f in inputs]

    return feature_names



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
    model_features = get_model_features()

    missing = [f for f in model_features if f not in scores]
    if missing:
        raise ValueError(f"❌ Faltan features requeridas por el modelo: {missing}")

    return {f: scores[f] for f in model_features}



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

