import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGO_URI = os.getenv("MONGO_URI")

# --- LISTAS DE CAMPOS A ESTANDARIZAR ---

# 1. Prefijos de preguntas tipo Likert (Deben ser ENTEROS: 1-5)
LIKERT_PREFIXES = [
    "EX", "AM", "CO", "NE", "AE", "ER", "AW", "PR", "CP", "SU", "FE", "FC", "DS"
]

# 2. Campos Demográficos (Deben ser ENTEROS, ya que guardamos IDs: 1, 2, 3...)
DEMO_FIELDS = [
    "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria", 
    "Demo_Tamano_Org", "Demo_Rol_Trabajo", "Demo_Generacion_Edad", 
    "Demo_Genero", "Demo_Nivel_Educacion", "Demo_Horas"
]

# 3. Scores calculados (Deben ser FLOAT/DECIMALES)
SCORE_PREFIXES = [
    "Big5_", "Phish_", "Fatiga_"
]

# 4. Campos del Modelo
FLOAT_FIELDS = ["probability"]
STRING_FIELDS = ["risk_level", "timestamp", "_id", "model_source"]

def to_int(val):
    """Intenta convertir a int. Si falla, devuelve None o 0."""
    try:
        if val is None or val == "":
            return 0
        return int(float(val)) # float() primero maneja strings como "5.0"
    except:
        return 0

def to_float(val):
    """Intenta convertir a float."""
    try:
        if val is None or val == "":
            return 0.0
        return float(val)
    except:
        return 0.0

def run_fix():
    print("🔧 Iniciando reparación de tipos de datos en MongoDB...")
    
    if not MONGO_URI:
        print("❌ Error: No se encontró MONGO_URI en .env")
        return

    client = MongoClient(MONGO_URI)
    db = client["PhishingDetectorDB"]
    collection = db["susceptibilidad"]
    
    # Obtener todos los documentos
    cursor = collection.find({})
    total_docs = collection.count_documents({})
    print(f"📂 Total de documentos a revisar: {total_docs}")
    
    updated_count = 0
    
    for doc in cursor:
        updates = {}
        
        # Recorremos todas las llaves del documento
        for key, value in doc.items():
            
            # A. Revisar si es Pregunta Likert (ej: EX01, AM05) -> INT
            # Comprobamos si la llave empieza con alguno de los prefijos
            if any(key.startswith(p) for p in LIKERT_PREFIXES) and len(key) <= 5:
                # Si no es int, lo convertimos
                if not isinstance(value, int):
                    updates[key] = to_int(value)

            # B. Revisar Demográficos -> INT
            elif key in DEMO_FIELDS:
                if not isinstance(value, int):
                    updates[key] = to_int(value)
            
            # C. Revisar Scores Calculados (Big5_...) -> FLOAT
            elif any(key.startswith(p) for p in SCORE_PREFIXES):
                if not isinstance(value, float):
                    updates[key] = to_float(value)
            
            # D. Probabilidad -> FLOAT
            elif key in FLOAT_FIELDS:
                if not isinstance(value, float):
                    updates[key] = to_float(value)
                    
            # E. Niveles de Riesgo -> STRING
            elif key in STRING_FIELDS:
                if not isinstance(value, str):
                    updates[key] = str(value)

        # Si hubo cambios, actualizamos el documento en la BD
        if updates:
            collection.update_one({"_id": doc["_id"]}, {"$set": updates})
            updated_count += 1
            
        if updated_count % 50 == 0 and updated_count > 0:
            print(f"   ...Corregidos {updated_count} documentos...")

    print("-" * 30)
    print(f"✅ Proceso terminado.")
    print(f"✨ Documentos corregidos/estandarizados: {updated_count}")

if __name__ == "__main__":
    run_fix()