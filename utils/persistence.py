import streamlit as st
import os
import uuid
import pytz
from datetime import datetime
from databricks import sql

# =========================
# 1. CONFIGURACIÓN DE COLUMNAS (CORREGIDA)
# ==========================================================

# A. Preguntas Individuales (RAW)
# IMPORTANTE: Ahora usamos formato con cero a la izquierda (01, 02...) 
# para coincidir con tu scoring.py
RAW_PREFIXES = [
    "EX", "AM", "CO", "NE", "AE",  # Big 5
    "ER", "AW", "PR", "CP", "SU",  # Phishing
    "FE", "FC", "DS"               # Fatiga
]

RAW_QUESTIONS_COLS = []
for pre in RAW_PREFIXES:
    # Generamos del 01 al 10 (ej: EX01...EX10)
    # Si alguna pregunta solo llega al 03 (como AW), el filtro de abajo lo manejará.
    for i in range(1, 11): 
        RAW_QUESTIONS_COLS.append(f"{pre}{i:02d}") # <--- AQUÍ ESTABA LA CLAVE (:02d)

# B. Scores Calculados (Tal cual tu scoring.py)
ALL_SCORES_COLS = [
    "Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad",
    "Big5_Neuroticismo", "Big5_Apertura",
    "Phish_Actitud_Riesgo", "Phish_Awareness", "Phish_Riesgo_Percibido",
    "Phish_Autoeficacia", "Phish_Susceptibilidad", "Fatiga_Global_Score"
]

# C. Demográficos
DEMO_COLS = [
    "Demo_Rol_Trabajo", "Demo_Horas", "Demo_Tamano_Org",
    "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria",
    "Demo_Genero", "Demo_Generacion_Edad", "Demo_Nivel_Educacion"
]

# D. Resultado Modelo
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
# INSERT PRINCIPAL
# =========================
def insert_survey_response(responses: dict, scores: dict, model_output: dict):
    
    # 1. Validar output mínimo
    if model_output.get("probability") is None:
        model_output["probability"] = 0.0

    # 2. Timestamp Chile
    tz_chile = pytz.timezone("America/Santiago")
    timestamp_to_save = datetime.now(tz_chile).replace(tzinfo=None)

    # 3. DICCIONARIO MAESTRO
    full_data = {
        "response_id": str(uuid.uuid4()),
        "timestamp": timestamp_to_save,
        **responses,      # Trae EX01, EX02...
        **scores,         # Trae Big5_Extraversion...
        **model_output    # Trae probability...
    }

    # 4. CONSTRUCCIÓN DE LA QUERY
    columns_to_insert = ["response_id", "timestamp"]
    values_to_insert = [full_data["response_id"], full_data["timestamp"]]

    # --- A. Preguntas Individuales (EX01, etc) ---
    for col in RAW_QUESTIONS_COLS:
        # Solo insertamos si la llave EXISTE en las respuestas.
        # Al usar :02d arriba, ahora sí coincidirá 'EX01' con 'EX01'.
        if col in full_data:
            columns_to_insert.append(col)
            values_to_insert.append(full_data[col])

    # --- B. Demográficos ---
    for col in DEMO_COLS:
        columns_to_insert.append(col)
        # Convertir a int si existe, sino -1
        val = full_data.get(col, -1)
        values_to_insert.append(int(val) if val is not None else -1)

    # --- C. Scores ---
    for col in ALL_SCORES_COLS:
        columns_to_insert.append(col)
        # Convertir a float, default 0.0
        val = full_data.get(col, 0.0)
        values_to_insert.append(float(val) if val is not None else 0.0)

    # --- D. Modelo ---
    for col in MODEL_COLS:
        columns_to_insert.append(col)
        values_to_insert.append(full_data.get(col))

    # 5. SQL STRING
    cols_str = ", ".join(columns_to_insert)
    placeholders = ", ".join(["?"] * len(columns_to_insert))
    
    sql_stmt = f"INSERT INTO phishing.surveys.responses ({cols_str}) VALUES ({placeholders})"

    # 6. EJECUTAR
    conn = get_connection_cached()
    cursor = conn.cursor()
    try:
        cursor.execute(sql_stmt, values_to_insert)
        if hasattr(conn, 'commit'):
            conn.commit()
        print("✅ Insert SQL exitoso") # Log para debug
    except Exception as e:
        print(f"❌ Error SQL: {e}")
        raise e # Re-lanzar para que lo vea el hilo
    finally:
        cursor.close()