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

def prepare_features(scores: dict, responses: dict) -> dict:
    """
    Prepara el payload JSON convirtiendo los datos de manera segura.
    Evita el error 'int() argument must be a string...'.
    """
    # 1. Recuperar valores crudos del diccionario de respuestas
    role_raw = responses.get("Demo_Rol_Trabajo")
    hours_raw = responses.get("Demo_Horas")

    # 2. VALIDACIÓN ESTRICTA: Si faltan datos, detenemos todo aquí
    # Esto previene que 'None' llegue a las funciones int() o float()
    if role_raw is None:
        raise ValueError("Error Crítico: El usuario no seleccionó su 'Rol de Trabajo'.")
    
    if hours_raw is None:
        raise ValueError("Error Crítico: El usuario no indicó sus 'Horas de uso'.")

    # 3. Conversión segura (ahora sabemos que NO son None)
    try:
        role_val = int(role_raw)
        hours_val = float(hours_raw)
    except (ValueError, TypeError) as e:
        # Si por alguna razón llegan datos corruptos que no son números
        raise ValueError(f"Error de tipo de datos: Rol='{role_raw}', Horas='{hours_raw}'. Detalle: {e}")

    # 4. Construcción del diccionario final
    features = {
        "Fatiga_Global_Score": float(scores.get("Fatiga_Global_Score", 0.0)),
        "Phish_Susceptibilidad": float(scores.get("Phish_Susceptibilidad", 0.0)),
        "Big5_Apertura": float(scores.get("Big5_Apertura", 0.0)),
        "Phish_Riesgo_Percibido": float(scores.get("Phish_Riesgo_Percibido", 0.0)),
        "Demo_Rol_Trabajo": role_val,
        "Demo_Horas": hours_val
    }

    return features

# =====================================================
# Predicción
# =====================================================

def predict(features: dict) -> dict:
    url = get_endpoint_url()
    headers = get_headers()

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
