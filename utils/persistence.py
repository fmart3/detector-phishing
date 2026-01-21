# utils/persistence.py
import streamlit as st
import os
import uuid
import time
import pytz
from datetime import datetime
from databricks import sql

# Quitamos la dependencia estricta de schema para evitar bloqueos
# from utils.schema import REQUIRED_RESPONSE_FIELDS 

# =========================
# CONEXIÓN
# =========================

@st.cache_resource(ttl=3600)
def get_connection_cached():
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )

# =========================
# INSERT ROBUSTO
# =========================
def insert_survey_response(responses: dict, scores: dict, model_output: dict):
    """
    Inserta datos manejando variables faltantes con valores por defecto (0 o -1).
    """
    
    # 1. Validación mínima
    if model_output.get("probability") is None:
        raise ValueError("Error: probability es nula.")

    # 2. Timestamp Chile
    tz_chile = pytz.timezone("America/Santiago")
    timestamp_to_save = datetime.now(tz_chile).replace(tzinfo=None)

    # 3. CONSTRUCCIÓN DE LA FILA (A PRUEBA DE KEY_ERRORS)
    # Aquí usamos .get(key, default) para TODO. Si falta algo, pone 0.
    
    row_data = {
        "response_id": str(uuid.uuid4()),
        "timestamp": timestamp_to_save,
        
        # --- Variables del Modelo Nuevo (Prioritarias) ---
        "Demo_Rol_Trabajo": int(responses.get("Demo_Rol_Trabajo", -1)),
        "Demo_Horas": int(responses.get("Demo_Horas", -1)),
        "Demo_Tamano_Org": int(responses.get("Demo_Tamano_Org", -1)),
        "Big5_Apertura": float(scores.get("Big5_Apertura", 0.0)),
        "Phish_Riesgo_Percibido": float(scores.get("Phish_Riesgo_Percibido", 0.0)),
        "Fatiga_Global_Score": float(scores.get("Fatiga_Global_Score", 0.0)),
        
        # --- Variables Antiguas (Relleno con defaults) ---
        # Demográficos viejos
        "Demo_Pais": int(responses.get("Demo_Pais", -1)),
        "Demo_Tipo_Organizacion": int(responses.get("Demo_Tipo_Organizacion", -1)),
        "Demo_Industria": int(responses.get("Demo_Industria", -1)),
        "Demo_Genero": int(responses.get("Demo_Genero", -1)),
        "Demo_Generacion_Edad": int(responses.get("Demo_Generacion_Edad", -1)),
        "Demo_Nivel_Educacion": int(responses.get("Demo_Nivel_Educacion", -1)),
        
        # Scores viejos (AQUÍ ESTABA TU ERROR)
        "Big5_Extraversion": float(scores.get("Big5_Extraversion", 0.0)),
        "Big5_Amabilidad": float(scores.get("Big5_Amabilidad", 0.0)),
        "Big5_Responsabilidad": float(scores.get("Big5_Responsabilidad", 0.0)),
        "Big5_Neuroticismo": float(scores.get("Big5_Neuroticismo", 0.0)),
        
        "Phish_Actitud_Riesgo": float(scores.get("Phish_Actitud_Riesgo", 0.0)),
        "Phish_Awareness": float(scores.get("Phish_Awareness", 0.0)),
        "Phish_Autoeficacia": float(scores.get("Phish_Autoeficacia", 0.0)),
        "Phish_Susceptibilidad": float(scores.get("Phish_Susceptibilidad", 0.0)),
        
        # --- Output Modelo ---
        "probability": float(model_output.get("probability", 0.0)),
        "risk_level": str(model_output.get("risk_level", "UNKNOWN"))
    }

    # 4. Lista de columnas en el orden EXACTO de la tabla SQL
    # IMPORTANTE: Asegúrate de que estos nombres coinciden con tu tabla en Databricks
    COLUMNS_ORDER = [
        "response_id", "timestamp",
        "Demo_Rol_Trabajo", "Demo_Horas", "Demo_Tamano_Org", 
        "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria", 
        "Demo_Genero", "Demo_Generacion_Edad", "Demo_Nivel_Educacion",
        "Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad",
        "Big5_Neuroticismo", "Big5_Apertura",
        "Phish_Actitud_Riesgo", "Phish_Awareness", "Phish_Riesgo_Percibido",
        "Phish_Autoeficacia", "Phish_Susceptibilidad", "Fatiga_Global_Score",
        "probability", "risk_level"
    ]

    values = [row_data[col] for col in COLUMNS_ORDER]
    
    # 5. Query
    columns_str = ", ".join(COLUMNS_ORDER)
    placeholders = ", ".join(["?"] * len(COLUMNS_ORDER))
    sql_stmt = f"INSERT INTO phishing.surveys.responses ({columns_str}) VALUES ({placeholders})"

    # 6. Ejecución
    conn = get_connection_cached()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_stmt, values)
        # En Databricks SQL Connector a veces es necesario commit, a veces es autocommit
        if hasattr(conn, 'commit'):
            conn.commit()
    finally:
        cursor.close()
        # No cerramos 'conn' porque usamos @st.cache_resource