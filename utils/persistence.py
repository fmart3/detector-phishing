import streamlit as st
import os
import uuid
import pytz
from datetime import datetime
from databricks import sql

# =========================
# CONFIGURACIÓN
# =========================

# Prefijos de preguntas
RAW_PREFIXES = [
    "EX", "AM", "CO", "NE", "AE",  # Big 5
    "ER", "AW", "PR", "CP", "SU",  # Phishing
    "FE", "FC", "DS"               # Fatiga
]

# Demográficos y Scores
DEMO_COLS = [
    "Demo_Rol_Trabajo", "Demo_Horas", "Demo_Tamano_Org",
    "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria",
    "Demo_Genero", "Demo_Generacion_Edad", "Demo_Nivel_Educacion"
]

ALL_SCORES_COLS = [
    "Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad",
    "Big5_Neuroticismo", "Big5_Apertura",
    "Phish_Actitud_Riesgo", "Phish_Awareness", "Phish_Riesgo_Percibido",
    "Phish_Autoeficacia", "Phish_Susceptibilidad", "Fatiga_Global_Score"
]

MODEL_COLS = ["probability", "risk_level"]

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
# INSERT INTELIGENTE
# =========================
def insert_survey_response(responses: dict, scores: dict, model_output: dict):
    
    # 1. Validar
    if model_output.get("probability") is None:
        model_output["probability"] = 0.0

    # 2. Timestamp
    tz_chile = pytz.timezone("America/Santiago")
    timestamp_to_save = datetime.now(tz_chile).replace(tzinfo=None)

    # 3. Diccionario Unificado
    full_data = {
        "response_id": str(uuid.uuid4()),
        "timestamp": timestamp_to_save,
        **responses,
        **scores,
        **model_output
    }

    columns_to_insert = ["response_id", "timestamp"]
    values_to_insert = [full_data["response_id"], full_data["timestamp"]]

    # --- A. PREGUNTAS INDIVIDUALES (Lógica Smart) ---
    found_count = 0
    
    for pre in RAW_PREFIXES:
        for i in range(1, 11): # 1 al 10
            # Nombres posibles
            db_col = f"{pre}{i:02d}"  # Formato DB (EX01)
            key_v1 = f"{pre}{i:02d}"  # Formato App v1 (EX01)
            key_v2 = f"{pre}{i}"      # Formato App v2 (EX1)
            
            val = None
            
            # Buscamos en orden de prioridad
            if key_v1 in full_data:
                val = full_data[key_v1]
            elif key_v2 in full_data:
                val = full_data[key_v2]
            
            # Si encontramos valor, agregamos a la query
            if val is not None:
                columns_to_insert.append(db_col) # Siempre usamos el nombre estandar DB
                values_to_insert.append(val)
                found_count += 1

    print(f"🔍 [Persistence] Se encontraron {found_count} respuestas individuales para insertar.")

    # --- B. Demográficos ---
    for col in DEMO_COLS:
        columns_to_insert.append(col)
        val = full_data.get(col, -1)
        values_to_insert.append(int(val) if val is not None else -1)

    # --- C. Scores ---
    for col in ALL_SCORES_COLS:
        columns_to_insert.append(col)
        val = full_data.get(col, 0.0)
        values_to_insert.append(float(val) if val is not None else 0.0)

    # --- D. Modelo ---
    for col in MODEL_COLS:
        columns_to_insert.append(col)
        values_to_insert.append(full_data.get(col))

    # 4. SQL EXECUTION
    cols_str = ", ".join(columns_to_insert)
    placeholders = ", ".join(["?"] * len(columns_to_insert))
    
    sql_stmt = f"INSERT INTO phishing.surveys.responses ({cols_str}) VALUES ({placeholders})"

    conn = get_connection_cached()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_stmt, values_to_insert)
        if hasattr(conn, 'commit'):
            conn.commit()
        print("✅ Insert SQL exitoso")
    except Exception as e:
        print(f"❌ Error SQL: {e}")
        raise e
    finally:
        cursor.close()