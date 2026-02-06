import os
import uuid
import pytz
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_chile_time():
    """Obtiene la hora actual en zona horaria de Chile."""
    chile_tz = pytz.timezone("America/Santiago")
    return datetime.now(chile_tz).strftime('%Y-%m-%d %H:%M:%S')

def get_mongo_collection():
    """Conecta a Mongo y devuelve la colección."""
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("❌ Error: MONGO_URI no encontrada en .env")
        return None
    
    try:
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        return db["susceptibilidad"]
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return None

def save_survey_response(raw_responses: dict, scores: dict, model_output: dict):
    """
    Guarda la encuesta como un documento JSON en MongoDB.
    """
    collection = get_mongo_collection()
    if collection is None:
        return False

    try:
        # 1. Construir el Documento (Diccionario único)
        record = {
            "_id": str(uuid.uuid4()),  # ID único para Mongo
            "timestamp": get_chile_time(),
            **raw_responses,           # Esparce respuestas (Demo_Pais, EX01...)
            **scores,                  # Esparce puntajes (Big5_..., Phish_...)
            "probability": float(model_output.get("probability", 0.0)),
            "risk_level": str(model_output.get("risk_level", "Error")),
            "model_source": model_output.get("source", "unknown")
        }

        # 2. Insertar en MongoDB
        result = collection.insert_one(record)
        
        print(f"✅ Documento guardado en MongoDB ID: {result.inserted_id}")
        return True

    except Exception as e:
        print(f"❌ Error guardando en MongoDB: {e}")
        return False