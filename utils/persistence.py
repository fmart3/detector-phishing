import uuid
import pytz
from datetime import datetime

def get_chile_time():
    """Obtiene la hora actual en zona horaria de Chile."""
    chile_tz = pytz.timezone("America/Santiago")
    return datetime.now(chile_tz).strftime('%Y-%m-%d %H:%M:%S')

def save_survey_response(collection, raw_responses: dict, scores: dict, model_output: dict):
    """
    Guarda la encuesta usando la colección de MongoDB que recibe como argumento.
    YA NO se conecta por sí mismo.
    """
    if collection is None:
        print("❌ Error: No hay conexión a la base de datos.")
        return False

    try:
        # 1. Construir el Documento
        record = {
            "_id": str(uuid.uuid4()),
            "timestamp": get_chile_time(),
            **raw_responses,
            **scores,
            "probability": float(model_output.get("probability", 0.0)),
            "risk_level": str(model_output.get("risk_level", "Error")),
            "model_source": model_output.get("source", "unknown")
        }

        # 2. Insertar usando la colección que nos pasaron
        result = collection.insert_one(record)
        
        print(f"✅ Documento guardado en MongoDB ID: {result.inserted_id}")
        return True

    except Exception as e:
        print(f"❌ Error guardando en MongoDB: {e}")
        return False