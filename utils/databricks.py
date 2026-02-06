import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
ENDPOINT_NAME = "phishing-endpoint" # Ajusta si tu endpoint tiene otro nombre

def get_endpoint_url():
    if not DATABRICKS_HOST:
        print("⚠️ Advertencia: No hay DATABRICKS_HOST en .env")
        return ""
    host = DATABRICKS_HOST.rstrip("/")
    return f"{host}/serving-endpoints/{ENDPOINT_NAME}/invocations"

def prepare_features(scores: dict, responses: dict):
    """
    Construye el payload EXACTO que pide el modelo con las 6 columnas específicas.
    Convierte strings a números.
    """
    
    # 1. Extraer y convertir datos con seguridad
    # Usamos try/except o valores por defecto para evitar errores si viene vacío
    try:
        demo_rol = int(responses.get("Demo_Rol_Trabajo", 0))
        fatiga_score = float(scores.get("Fatiga_Global_Score", 0.0))
        big5_apertura = float(scores.get("Big5_Apertura", 0.0))
        riesgo_percibido = float(scores.get("Phish_Riesgo_Percibido", 0.0))
        demo_horas = int(responses.get("Demo_Horas", 0))
        demo_tamano = int(responses.get("Demo_Tamano_Org", 0))
    except ValueError as e:
        print(f"❌ Error convirtiendo datos para el modelo: {e}")
        # Valores por defecto en caso de error de conversión
        demo_rol, fatiga_score, big5_apertura, riesgo_percibido, demo_horas, demo_tamano = 0, 0.0, 0.0, 0.0, 0, 0

    # 2. Definir columnas y datos en el orden estricto del modelo
    columns = [
        "Demo_Rol_Trabajo",
        "Fatiga_Global_Score",
        "Big5_Apertura",
        "Phish_Riesgo_Percibido",
        "Demo_Horas",
        "Demo_Tamano_Org"
    ]
    
    data_row = [
        demo_rol,
        fatiga_score,
        big5_apertura,
        riesgo_percibido,
        demo_horas,
        demo_tamano
    ]

    # 3. Estructura 'dataframe_split'
    payload = {
        "dataframe_split": {
            "columns": columns,
            "data": [data_row]
        }
    }
    
    return payload

def predict_model(payload):
    """
    Envía el payload al Endpoint y procesa la respuesta.
    """
    url = get_endpoint_url()
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"📡 Enviando al modelo: {json.dumps(payload)}") # Debug
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP Modelo ({response.status_code}): {response.text}")
            return {"probability": 0.0, "risk_level": "Error HTTP"}
            
        result = response.json()
        print(f"📥 Respuesta cruda modelo: {result}") # Debug

        # Procesamos la respuesta según tu ejemplo:
        # { "predictions": [ { "prediction": 0, "probability": 0.37... } ] }
        predictions_list = result.get("predictions", [])
        
        if predictions_list:
            first_pred = predictions_list[0] # Tomamos el primer objeto
            
            # Extraemos la probabilidad
            prob = first_pred.get("probability", 0.0)
            
            # Determinamos el nivel de riesgo (Regla de negocio simple)
            risk = "ALTO" if prob > 0.7 else "MEDIO" if prob > 0.4 else "BAJO"
            
            return {
                "probability": float(prob),
                "risk_level": risk,
                "model_raw": first_pred # Guardamos esto para debug
            }
        
        return {"probability": 0.0, "risk_level": "Respuesta vacía"}
            
    except Exception as e:
        print(f"❌ Excepción conectando al modelo: {e}")
        return {"probability": 0.0, "risk_level": "Error Conexión"}