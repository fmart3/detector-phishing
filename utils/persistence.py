# utils/persistence.py
import os
import uuid
from datetime import datetime
from databricks import sql

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

    # ---- Construcción de la fila
    row = {
        "response_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow(),
    }

    # Respuestas (todas las preguntas)
    row.update(responses)

    # Scores
    row.update(scores)

    # Modelo
    row["probability"] = model_output.get("probability")
    row["risk_level"] = model_output.get("risk_level")

    # ---- Inserción SQL
    conn = get_connection()
    cursor = conn.cursor()

    columns = ", ".join(row.keys())
    placeholders = ", ".join(["?"] * len(row))

    sql_stmt = f"""
        INSERT INTO phishing.surveys.responses ({columns})
        VALUES ({placeholders})
    """

    cursor.execute(sql_stmt, list(row.values()))
    conn.commit()

    cursor.close()
    conn.close()
