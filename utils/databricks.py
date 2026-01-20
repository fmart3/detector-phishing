import requests
import streamlit as st

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "phishing-endpoint"

# Lista exacta de features que espera el modelo actual
MODEL_FEATURES = [
    "Demo_Tamano_Org",
    "Demo_Rol_Trabajo",
    "Big5_Apertura",
    "Demo_Horas",
    "Phish_Riesgo_Percibido",
    "Fatiga_Global_Score"
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
    Prepara el payload JSON con los 6 features exactos que pide el modelo.
    """
    # 1. Recuperar valores crudos de las respuestas demográficas
    role_raw = responses.get("Demo_Rol_Trabajo")
    hours_raw = responses.get("Demo_Horas")
    size_raw = responses.get("Demo_Tamano_Org") # Nuevo feature

    # 2. VALIDACIÓN ESTRICTA
    if role_raw is None:
        raise ValueError("Error Crítico: El usuario no seleccionó su 'Rol de Trabajo'.")
    
    if hours_raw is None:
        raise ValueError("Error Crítico: El usuario no indicó sus 'Horas de uso'.")
        
    if size_raw is None:
        raise ValueError("Error Crítico: El usuario no indicó el 'Tamaño de la Organización'.")

    # 3. Conversión segura de tipos
    try:
        role_val = int(role_raw)
        hours_val = float(hours_raw)
        size_val = int(size_raw) # Convertimos tamaño a entero
    except (ValueError, TypeError) as e:
        raise ValueError(f"Error de tipo de datos en demográficos. Detalle: {e}")

    # 4. Construcción del diccionario final (Orden no importa en JSON, pero ayuda a la lectura)
    features = {
        "Demo_Tamano_Org": size_val,
        "Demo_Rol_Trabajo": role_val,
        "Big5_Apertura": float(scores.get("Big5_Apertura", 0.0)),
        "Demo_Horas": hours_val,
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

    # Formato 'dataframe_records' es el estándar para Databricks Serving con pandas
    payload = {
        "dataframe_records": [features]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión con Databricks: {e}")
        st.stop()

    if response.status_code != 200:
        st.error("❌ Error al invocar endpoint Databricks")
        st.code(response.text)
        st.stop()

    result = response.json()
    
    # Manejo robusto de la respuesta (dependiendo de si viene con wrapper o cruda)
    if "predictions" in result:
        prediction_row = result["predictions"][0]

        # Caso A: Modelo con Wrapper (devuelve diccionario)
        if isinstance(prediction_row, dict):
            # Buscamos 'prediction' (int) y 'probability' (float)
            pred_class = int(prediction_row.get("prediction", 0))
            probability = prediction_row.get("probability") 
            if probability is not None:
                probability = float(probability)
        
        # Caso B: Modelo crudo (devuelve solo el valor predicho)
        else:
            pred_class = int(prediction_row)
            probability = None
    else:
        # Caso raro: formato inesperado
        st.error("Formato de respuesta de Databricks desconocido")
        st.write(result)
        st.stop()

    return {
        "prediction": pred_class,
        "probability": probability
    }