# utils/persistence.py
import streamlit as st
import os
import uuid
import time
import pytz
from datetime import datetime
from databricks import sql
from databricks.sql.exc import Error as DatabricksSqlError

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
# DEFINICIÓN DE COLUMNAS (Manual para seguridad)
# =========================
# Estas son TODAS las columnas que tu tabla en Databricks espera.
ALL_DB_COLUMNS = [
    "response_id", "timestamp",
    # Demográficos (Los 6 del simulador + los viejos que faltan)
    "Demo_Rol_Trabajo", "Demo_Horas", "Demo_Tamano_Org", 
    "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria", 
    "Demo_Genero", "Demo_Generacion_Edad", "Demo_Nivel_Educacion",
    # Scores Numéricos
    "Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad",
    "Big5_Neuroticismo", "Big5_Apertura",
    "Phish_Actitud_Riesgo", "Phish_Awareness", "Phish_Riesgo_Percibido",
    "Phish_Autoeficacia", "Phish_Susceptibilidad", "Fatiga_Global_Score",
    # Resultado Modelo
    "probability", "risk_level"
]

# =========================
# INSERT PRINCIPAL
# =========================

def insert_survey_response(responses: dict, scores: dict, model_output: dict):
    """
    Inserta una fila en phishing.surveys.responses manejando datos faltantes.
    """
    
    # 1. Validar output del modelo esencial
    if model_output.get("probability") is None:
        raise ValueError("Error crítico: 'probability' es nula.")

    # 2. Generar Timestamp Chile
    tz_chile = pytz.timezone("America/Santiago")
    now_chile = datetime.now(tz_chile)
    timestamp_to_save = now_chile.replace(tzinfo=None) # Naive para SQL

    # 3. CONSTRUCCIÓN ROBUSTA DE LA FILA (Evita KeyErrors)
    # Creamos un diccionario maestro con TODO lo que pueda venir
    
    full_data = {
        "response_id": str(uuid.uuid4()),
        "timestamp": timestamp_to_save,
        **responses,      # Demo_Rol, Demo_Horas, Demo_Tamano
        **scores,         # Scores calculados
        **model_output    # probability, risk_level
    }

    # 4. Preparar valores ordenados según la tabla
    values = []
    for col in ALL_DB_COLUMNS:
        # TRUCO: .get(col, -1)
        # Si la columna existe (ej: Demo_Rol_Trabajo), usa el valor.
        # Si NO existe (ej: Demo_Pais, porque ya no lo preguntas), pone -1 o 0.0.
        
        val = full_data.get(col)
        
        if val is None:
            # Asignar defaults si falta el dato para que SQL no falle
            if col.startswith("Demo_"): val = -1
            elif col.startswith("Big5_") or col.startswith("Phish_") or col.startswith("Fatiga_"): val = 0.0
            else: val = None # Strings u otros
            
        values.append(val)

    # 5. Query SQL Dinámica
    columns_str = ", ".join(ALL_DB_COLUMNS)
    placeholders = ", ".join(["?"] * len(ALL_DB_COLUMNS))

    sql_stmt = f"""
        INSERT INTO phishing.surveys.responses ({columns_str})
        VALUES ({placeholders})
    """
        
    # 6. Ejecución con Retries
    MAX_RETRIES = 3
    for attempt in range(1, MAX_RETRIES + 1):
        conn = None
        cursor = None
        try:
            conn = get_connection_cached()
            cursor = conn.cursor()
            
            # Ejecutar
            cursor.execute(sql_stmt, values)
            
            # Commit y Cerrar Cursor
            if hasattr(conn, 'commit'):
                conn.commit()
            
            cursor.close()
            print(f"✅ [DB] Insert exitoso (Intento {attempt})")
            return # Éxito, salimos de la función

        except Exception as e:
            print(f"⚠️ [DB] Fallo intento {attempt}: {e}")
            
            # Si falló la conexión, limpiamos caché para el siguiente intento
            if "closed" in str(e).lower() or "connection" in str(e).lower():
                st.cache_resource.clear()
            
            if attempt == MAX_RETRIES:
                # Si falló el último intento, lanzamos el error para que lo vea el Thread
                raise RuntimeError(f"Error final DB: {e}")
            
            time.sleep(1)
        
        finally:
            # Aseguramos limpieza si quedó abierto algo
            try:
                if cursor: cursor.close()
                if conn: conn.close()
            except: pass