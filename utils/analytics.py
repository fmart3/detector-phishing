import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_dashboard_stats():
    """
    Conecta a MongoDB, descarga las encuestas y calcula métricas avanzadas
    para el dashboard visual.
    """
    uri = os.getenv("MONGO_URI")
    
    if not uri:
        print("❌ Error: MONGO_URI no configurada.")
        return {}

    try:
        # 1. Conexión a Mongo
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        collection = db["susceptibilidad"]

        # 2. Traer datos (Excluimos _id para limpieza)
        # Traemos todo porque necesitamos calcular promedios de Big5, Fatiga, etc.
        cursor = collection.find({}, {"_id": 0})
        data = list(cursor)
        
        # Si no hay datos, retornamos estructura vacía segura
        if not data:
            return {
                "total_responses": 0, 
                "average_probability": 0, 
                "risk_distribution": {"BAJO": 0, "MEDIO": 0, "ALTO": 0},
                "big5_averages": [0,0,0,0,0],
                "factors_averages": [0,0]
            }

        # 3. Convertir a DataFrame para análisis rápido
        df = pd.DataFrame(data)
        
        # --- A. Métricas Generales ---
        total = len(df)
        avg_prob = float(df["probability"].mean()) if "probability" in df.columns else 0.0
        
        # --- B. Distribución de Riesgo ---
        # .get para evitar error si la columna no existe aún
        risk_counts = df["risk_level"].value_counts().to_dict() if "risk_level" in df.columns else {}
        
        # Asegurar que existan las 3 llaves aunque sean 0
        risk_distribution = {
            "BAJO": risk_counts.get("BAJO", 0),
            "MEDIO": risk_counts.get("MEDIO", 0),
            "ALTO": risk_counts.get("ALTO", 0)
        }

        # --- C. Promedios de Personalidad (Big 5) ---
        # El orden para el gráfico Radar: [Extraversión, Amabilidad, Responsabilidad, Neuroticismo, Apertura]
        big5_cols = [
            "Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad", 
            "Big5_Neuroticismo", "Big5_Apertura"
        ]
        
        # Calculamos media, rellenando nulos con 0
        big5_scores = []
        for col in big5_cols:
            val = df[col].mean() if col in df.columns else 0
            big5_scores.append(round(val, 2))

        # --- D. Factores de Riesgo (Fatiga vs Susceptibilidad) ---
        fatiga_avg = df["Fatiga_General"].mean() if "Fatiga_General" in df.columns else 0
        suscept_avg = df["Phish_Susceptibilidad"].mean() if "Phish_Susceptibilidad" in df.columns else 0
        
        return {
            "total_responses": total,
            "average_probability": round(avg_prob, 2),
            "risk_distribution": risk_distribution,
            "big5_averages": big5_scores,
            "factors_averages": [round(fatiga_avg, 2), round(suscept_avg, 2)]
        }

    except Exception as e:
        print(f"❌ Error en analytics.py: {e}")
        return {}