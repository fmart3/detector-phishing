import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_dashboard_stats():
    """
    Descarga datos desde MongoDB y calcula estadísticas.
    """
    uri = os.getenv("MONGO_URI")
    
    try:
        # 1. Conexión
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        collection = db["susceptibilidad"]

        # 2. Obtener solo los campos necesarios (Proyección para optimizar)
        # Traemos risk_level y probability. _id=0 para no traer el ID.
        cursor = collection.find({}, {"_id": 0, "risk_level": 1, "probability": 1})
        
        # Convertir cursor a lista y luego a DataFrame
        data = list(cursor)
        
        if not data:
            return {"total_responses": 0, "average_probability": 0, "risk_distribution": {}}

        df = pd.DataFrame(data)
        
        # 3. Cálculos (Igual que antes)
        total = len(df)
        avg_prob = float(df["probability"].mean()) if not df.empty else 0.0
        
        # Conteo de riesgo
        risk_counts = df["risk_level"].value_counts().to_dict()
        
        return {
            "total_responses": total,
            "average_probability": round(avg_prob, 2),
            "risk_distribution": risk_counts
        }

    except Exception as e:
        print(f"❌ Error Analytics MongoDB: {e}")
        return {"error": str(e)}