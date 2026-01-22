# /utils/databricks.py

import requests
import pandas as pd
import streamlit as st
from databricks import sql  # <--- NUEVA IMPORTACIÓN (pip install databricks-sql-connector)

# =====================================================
# Configuración
# =====================================================

DATABRICKS_ENDPOINT = "phishing-endpoint" 

def get_config():
    """Recupera configuración básica"""
    try:
        token = st.secrets["DATABRICKS_TOKEN"]
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
# 🧠 PARTE 1: INFERENCIA (Para el modelo)
# =====================================================
# ... (Mantén aquí tus funciones prepare_features y predict tal cual las tienes) ...

def prepare_features(scores: dict, responses: dict):
    # ... (Tu código actual de prepare_features) ...
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
        raise ValueError(f"Error procesando tipos de datos: {e}")
    return pd.DataFrame(data)

def predict(feature_df):
    # ... (Tu código actual de predict, está perfecto) ...
    token, host = get_config()
    if not token or not host: return {"prediction": 0, "probability": 0.0}
    
    url = get_endpoint_url(host)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"dataframe_split": feature_df.to_dict(orient="split")}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ Error API: {response.text}")
            return {"prediction": 0, "probability": 0.0}
        
        result = response.json()
        predictions = result.get("predictions", [])
        if len(predictions) > 0:
            first = predictions[0]
            if isinstance(first, dict):
                return {"prediction": int(first.get("prediction", 0)), "probability": float(first.get("probability", 0.0))}
            else:
                return {"prediction": int(first), "probability": 0.0}
        return {"prediction": 0, "probability": 0.0}
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return {"prediction": 0, "probability": 0.0}


# =====================================================
# 📊 PARTE 2: ANALÍTICA (Para el Dashboard)
# =====================================================

@st.cache_data(ttl=600, show_spinner=False)  # <--- ¡LA CLAVE! Cachea por 10 minutos
def run_sql_query(query: str):
    """
    Ejecuta SQL en Databricks Warehouse y devuelve un DataFrame.
    Usa caché para no saturar la conexión en cada recarga.
    """
    
    # Verificamos el HTTP PATH (necesario solo para SQL, no para el modelo)
    if "DATABRICKS_HTTP_PATH" not in st.secrets:
        st.error("❌ Falta 'DATABRICKS_HTTP_PATH' en secrets.toml para el Dashboard.")
        return pd.DataFrame()

    token, host = get_config() # Reusamos tu función de config
    
    if not token or not host:
        return pd.DataFrame()

    try:
        # Limpiamos el host para el conector SQL (no le gusta el https://)
        server_hostname = host.replace("https://", "").replace("http://", "")

        with sql.connect(
            server_hostname=server_hostname,
            http_path=st.secrets["DATABRICKS_HTTP_PATH"],
            access_token=token
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    return pd.DataFrame(result, columns=columns)
                return pd.DataFrame()
                
    except Exception as e:
        st.error(f"Error conectando a Databricks SQL: {e}")
        return pd.DataFrame()