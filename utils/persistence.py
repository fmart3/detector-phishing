import os
import uuid
from datetime import datetime
import pytz
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

def get_chile_time():
    """Obtiene la hora actual en zona horaria de Chile (Santiago)."""
    chile_tz = pytz.timezone("America/Santiago")
    # Formato ISO 8601 compatible con Databricks timestamp
    return datetime.now(chile_tz).strftime('%Y-%m-%d %H:%M:%S')

def insert_response_sql(raw_responses: dict, scores: dict, model_output: dict):
    """
    Guarda los datos en Databricks SQL asegurando que coincidan con las columnas de la tabla.
    """
    
    # 1. Configuración
    host = os.getenv("DATABRICKS_HOST").replace("https://", "").replace("http://", "").rstrip("/")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")
    
    TABLE_NAME = "phishing.surveys.responses" 

    # 2. CONSTRUCCIÓN DEL REGISTRO EXACTO
    # Creamos un diccionario nuevo explícitamente para no meter basura
    
    record = {}

    # A. Identificadores (CORREGIDO: response_id en lugar de session_id)
    record["response_id"] = str(uuid.uuid4()) 
    record["timestamp"] = get_chile_time()

    # B. Respuestas (EX01, Demo_Pais, etc.)
    # Pasamos todo raw_responses, asumiendo que las llaves coinciden con las columnas
    record.update(raw_responses)

    # C. Scores (Big5_..., Phish_...)
    record.update(scores)

    # D. Modelo (FILTRADO: Solo pasamos lo que existe en la tabla)
    # Evitamos pasar 'model_raw' u otros datos de debug
    record["probability"] = float(model_output.get("probability", 0.0))
    record["risk_level"] = str(model_output.get("risk_level", "Error"))

    # 3. Construcción de la Query Dinámica
    columns = list(record.keys())
    values = list(record.values())

    # Generamos placeholders (?, ?, ?)
    placeholders = ", ".join(["?"] * len(columns))
    columns_str = ", ".join(columns)
    
    query = f"INSERT INTO {TABLE_NAME} ({columns_str}) VALUES ({placeholders})"

    # 4. Ejecución
    print(f"💾 Insertando {len(columns)} columnas en SQL...")
    
    try:
        with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
        
        print(f"✅ Guardado exitoso. ID: {record['response_id']}")
        return True
        
    except Exception as e:
        print(f"❌ Error CRÍTICO guardando en SQL: {e}")
        # Tip de debug: Imprimir qué columna podría estar sobrando o faltando
        # print("Columnas enviadas:", columns)
        return False