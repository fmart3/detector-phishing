# utils/persistence.py
import os
import uuid
import time
import pytz
from datetime import datetime
from databricks import sql
from databricks.sql.exc import Error as DatabricksSqlError
from utils.schema import REQUIRED_RESPONSE_FIELDS


# =========================
# CONEXIÓN
# =========================

def get_connection():
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )


# =========================
# VALIDACIONES
# =========================

def validate_responses(responses: dict):
    missing = [k for k in REQUIRED_RESPONSE_FIELDS if k not in responses]
    if missing:
        raise ValueError(f"Faltan respuestas obligatorias: {missing}")

def validate_ranges(responses: dict):
    for k, v in responses.items():

        if v is None:
            raise ValueError(f"Respuesta nula en {k}")

        if not isinstance(v, (int, float)):
            raise ValueError(f"Tipo inválido en {k}: {type(v)}")

        # Likert 1–5
        if k.startswith(("EX","AM","CO","NE","AE","ER","AW","PR","CP","SU","FE","FC","DS")):
            if not 1 <= v <= 5:
                raise ValueError(f"Valor fuera de rango en {k}: {v}")

        # Demográficos
        if k.startswith("Demo_"):
            if v < 0:
                raise ValueError(f"Valor demográfico inválido en {k}: {v}")


# =========================
# INSERT PRINCIPAL
# =========================

def insert_survey_response(
    responses: dict,
    scores: dict,
    model_output: dict
):
    """
    Inserta una fila completa en phishing.surveys.responses
    """

    # ---- Validaciones
    validate_responses(responses)
    validate_ranges(responses)
    
    if model_output.get("probability") is None:
        raise ValueError("probability no puede ser nula")
    
    # ============================================================
    # 2. CALCULAR HORA CHILE
    # ============================================================
    # Definimos la zona horaria
    tz_chile = pytz.timezone("America/Santiago")
    
    # Obtenemos la hora actual en Chile
    now_chile = datetime.now(tz_chile)
    
    # TRUCO IMPORTANTE:
    # Las bases de datos a veces reconvierten a UTC si detectan zona horaria.
    # Para forzar que se guarde "15:00" (hora Chile) y no se transforme,
    # le quitamos la info de zona horaria (hacemos el datetime "naive").
    timestamp_to_save = now_chile.replace(tzinfo=None)
    
    row = {
        "response_id": str(uuid.uuid4()),
        "timestamp": timestamp_to_save,
        **responses,
        **scores,
        "probability": model_output.get("probability"),
        "risk_level": model_output.get("risk_level"),
    }
    
    TABLE_COLUMNS = (
        ["response_id", "timestamp"]
        + REQUIRED_RESPONSE_FIELDS
        + [
            "Big5_Extraversion",
            "Big5_Amabilidad",
            "Big5_Responsabilidad",
            "Big5_Neuroticismo",
            "Big5_Apertura",
            "Phish_Actitud_Riesgo",
            "Phish_Awareness",
            "Phish_Riesgo_Percibido",
            "Phish_Autoeficacia",
            "Phish_Susceptibilidad",
            "Fatiga_Global_Score",
            "probability",
            "risk_level",
        ]
    )
    
    columns = ", ".join(TABLE_COLUMNS)
    placeholders = ", ".join(["?"] * len(TABLE_COLUMNS))
    values = [row[col] for col in TABLE_COLUMNS]

    sql_stmt = f"""
        INSERT INTO phishing.surveys.responses ({columns})
        VALUES ({placeholders})
    """
        
    # Retries suaves y Manejo errores SQL
    
    MAX_RETRIES = 3

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql_stmt, values)
            conn.commit()
            break
        except DatabricksSqlError as e:  # <--- CORREGIDO AQUÍ (coincide con el import)
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Error insertando respuesta tras {MAX_RETRIES} intentos: {e}"
                ) from e
            time.sleep(0.5 * attempt)
        finally:
            # Es buena práctica verificar si 'conn' o 'cursor' existen antes de cerrarlos
            # en caso de que la conexión falle antes de crearse.
            try:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()
            except:
                pass