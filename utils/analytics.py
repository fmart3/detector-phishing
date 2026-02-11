import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_dashboard_stats():
    uri = os.getenv("MONGO_URI")
    if not uri: return {"error": "MONGO_URI missing"}

    try:
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        collection = db["susceptibilidad"]
        
        data = list(collection.find({}, {"_id": 0}))
        if not data: return {"empty": True}

        df = pd.DataFrame(data)
        
        # 1. Limpieza y Conversión Numérica General
        # Definimos las columnas que queremos disponibles para el Scatter Plot
        # Incluimos Scores, Big5 y Demográficos numéricos
        target_cols = [
            "probability", "Fatiga_Global_Score", "Phish_Susceptibilidad", 
            "Demo_Horas", "Demo_Tamano_Org", 
            "Big5_Apertura", "Big5_Responsabilidad", "Big5_Extraversion", 
            "Big5_Amabilidad", "Big5_Neuroticismo"
        ]

        # Asegurar que existan y sean números (rellenar con 0 si faltan)
        for col in target_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- A. VEREDICTO DE SALUD ---
        probs = df["probability"]
        std_dev = probs.std()
        r_range = probs.max() - probs.min()
        
        model_health = {
            "status": "SALUDABLE" if std_dev > 0.05 else "ESTABLE",
            "color": "success" if std_dev > 0.05 else "warning",
            "message": "Varianza detectada." if std_dev > 0.05 else "Poca variabilidad.",
            "metrics": {
                "std": round(float(std_dev), 3) if not pd.isna(std_dev) else 0,
                "min": round(float(probs.min()), 2),
                "max": round(float(probs.max()), 2)
            }
        }

        # --- B. Datos Completos para Scatter Dinámico ---
        # Enviamos todas las columnas numéricas + risk_level para el color
        # Convertimos a diccionario orientado a registros
        scatter_payload = df[target_cols + ["risk_level"]].to_dict(orient="records")

        # --- C. Histograma ---
        hist_counts, _ = np.histogram(df["probability"], bins=10, range=(0, 1))
        
        # --- D. Radar Big 5 ---
        big5_avgs = [round(df[c].mean(), 2) for c in target_cols if "Big5" in c]

        # --- KPI Counts ---
        risk_counts = df["risk_level"].value_counts().to_dict() if "risk_level" in df.columns else {}

        return {
            "empty": False,
            "total_responses": len(df),
            "avg_risk": round(probs.mean() * 100, 1),
            "risk_counts": {k: risk_counts.get(k, 0) for k in ["ALTO", "MEDIO", "BAJO"]},
            "health_check": model_health,
            "histogram": {
                "labels": ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"],
                "data": hist_counts.tolist()
            },
            "big5_radar": {
                "labels": ["Apertura", "Responsabilidad", "Extraversion", "Amabilidad", "Neuroticismo"],
                "data": big5_avgs
            },
            "scatter_full_data": scatter_payload, # <--- NUEVA DATA COMPLETA
            "raw_data": df.tail(50).to_dict(orient="records")
        }

    except Exception as e:
        print(f"❌ Error Analytics: {e}")
        return {"error": str(e)}