import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_dashboard_stats():
    """
    Backend analítico completo: Conecta a Mongo, procesa estadísticas 
    avanzadas (Histogramas, Scatter, Big5) y prepara datos para la web.
    """
    uri = os.getenv("MONGO_URI")
    if not uri:
        return {"error": "MONGO_URI missing"}

    try:
        # 1. Conexión a MongoDB
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        collection = db["susceptibilidad"]
        
        # Traemos todo (excluyendo _id para evitar problemas de JSON)
        data = list(collection.find({}, {"_id": 0}))
        
        if not data:
            return {"empty": True}

        df = pd.DataFrame(data)
        
        # 2. Limpieza de Datos (Asegurar numéricos)
        # Nota: Usamos 'Fatiga_Global_Score' que es el nombre correcto en scoring.py
        cols_to_check = ["probability", "Fatiga_Global_Score", "Phish_Susceptibilidad"]
        for col in cols_to_check:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- A. VEREDICTO DE SALUD DEL MODELO ---
        probs = df["probability"]
        std_dev = probs.std()
        r_min = probs.min()
        r_max = probs.max()
        r_range = r_max - r_min
        
        model_health = {
            "status": "CRITICO",
            "color": "danger",
            "message": "El modelo no detecta variabilidad. Posible error de datos.",
            "metrics": {
                "std": round(float(std_dev), 3) if not pd.isna(std_dev) else 0,
                "range": round(float(r_range), 2),
                "min": round(float(r_min), 2),
                "max": round(float(r_max), 2)
            }
        }

        if std_dev > 0.05 and r_range > 0.3:
            model_health["status"] = "SALUDABLE"
            model_health["color"] = "success"
            model_health["message"] = "Varianza saludable. El modelo distingue bien los riesgos."
        elif std_dev > 0.02:
            model_health["status"] = "ESTABLE"
            model_health["color"] = "warning"
            model_health["message"] = "Poca variabilidad. Revisa si las preguntas discriminan suficiente."

        # --- B. Datos para Scatter Plot (Fatiga vs Probabilidad) ---
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                "x": round(row.get("Fatiga_Global_Score", 0), 2), # Corregido nombre columna
                "y": round(row.get("probability", 0), 2),
                "r": row.get("risk_level", "BAJO") 
            })

        # --- C. Datos para Histograma (Probabilidades) ---
        hist_counts, _ = np.histogram(df["probability"], bins=10, range=(0, 1))
        
        # --- D. Datos para Radar (Big 5) ---
        big5_cols = ["Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad", "Big5_Neuroticismo", "Big5_Apertura"]
        big5_avgs = []
        for c in big5_cols:
            val = df[c].mean() if c in df.columns else 0
            big5_avgs.append(round(val, 2))

        # --- E. KPIs Generales ---
        risk_counts = df["risk_level"].value_counts().to_dict() if "risk_level" in df.columns else {}
        
        # --- CONSTRUCCIÓN DEL JSON FINAL ---
        return {
            "empty": False,
            "total_responses": len(df),
            "avg_risk": round(probs.mean() * 100, 1),
            "risk_counts": {
                "ALTO": risk_counts.get("ALTO", 0),
                "MEDIO": risk_counts.get("MEDIO", 0),
                "BAJO": risk_counts.get("BAJO", 0)
            },
            "health_check": model_health,
            "histogram": {
                "labels": ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"],
                "data": hist_counts.tolist()
            },
            "big5_radar": {
                "labels": ["Extraversión", "Amabilidad", "Responsabilidad", "Neuroticismo", "Apertura"],
                "data": big5_avgs
            },
            "scatter_data": scatter_data, # ¡AQUÍ FALTABA ESTO!
            "raw_data": df.tail(50).to_dict(orient="records")
        }

    except Exception as e:
        print(f"❌ Error Analytics: {e}")
        return {"error": str(e)}