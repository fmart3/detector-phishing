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
        # 1. Conexión
        client = MongoClient(uri)
        db = client["PhishingDetectorDB"]
        collection = db["susceptibilidad"]
        
        # Traemos todo (excluyendo _id)
        data = list(collection.find({}, {"_id": 0}))
        
        if not data:
            return {"empty": True}

        df = pd.DataFrame(data)
        
        # Asegurar columnas numéricas (rellenar nulos con 0)
        cols_to_check = ["probability", "Fatiga_General", "Phish_Susceptibilidad"]
        for col in cols_to_check:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # --- A. KPIs Generales ---
        risk_counts = df["risk_level"].value_counts().to_dict() if "risk_level" in df.columns else {}
        risk_dist = {
            "BAJO": risk_counts.get("BAJO", 0),
            "MEDIO": risk_counts.get("MEDIO", 0),
            "ALTO": risk_counts.get("ALTO", 0)
        }

        # --- B. Datos para Radar (Big 5) ---
        big5_cols = ["Big5_Extraversion", "Big5_Amabilidad", "Big5_Responsabilidad", "Big5_Neuroticismo", "Big5_Apertura"]
        big5_avgs = []
        for c in big5_cols:
            val = df[c].mean() if c in df.columns else 0
            big5_avgs.append(round(val, 2))

        # --- C. Datos para Histograma (Probabilidades) ---
        # Usamos numpy para calcular los "bins" (cubos) del histograma en el servidor
        hist_counts, hist_edges = np.histogram(df["probability"], bins=10, range=(0, 1))
        # Formateamos etiquetas ej: "0.0-0.1"
        hist_labels = [f"{hist_edges[i]:.1f}-{hist_edges[i+1]:.1f}" for i in range(len(hist_edges)-1)]

        # --- D. Datos para Scatter Plot (Fatiga vs Probabilidad) ---
        # Enviamos un array ligero solo con X, Y y Color para el gráfico
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                "x": round(row.get("Fatiga_General", 0), 2),
                "y": round(row.get("probability", 0), 2),
                "r": row.get("risk_level", "BAJO") # Para colorear en frontend
            })

        # --- E. Estadísticas Avanzadas (Salud del Modelo) ---
        probs = df["probability"]
        std_dev = probs.std()
        r_min = probs.min()
        r_max = probs.max()
        
        # Veredicto de Salud
        verdict = "SALUDABLE"
        verdict_msg = "El modelo discrimina correctamente entre usuarios seguros y riesgosos."
        verdict_color = "success" # verde
        
        if std_dev < 0.02:
            verdict = "PLANO"
            verdict_msg = "El modelo está estancado (baja varianza). Todos reciben casi el mismo puntaje."
            verdict_color = "danger"
        elif (r_max - r_min) < 0.1:
            verdict = "RANGO CORTO"
            verdict_msg = "El modelo no distingue extremos. Revisa los pesos de scoring."
            verdict_color = "warning"

        # --- F. Datos Crudos (Últimos 100 para tabla) ---
        # Convertimos a dict 'records' para enviarlo fácil a JS
        # Ordenamos por timestamp si existe, sino tomamos los últimos
        if "timestamp" in df.columns:
            raw_table = df.sort_values("timestamp", ascending=False).head(100).to_dict(orient="records")
        else:
            raw_table = df.tail(100).to_dict(orient="records")

        return {
            "empty": False,
            "total_responses": len(df),
            "average_probability": round(probs.mean(), 2),
            "risk_distribution": risk_dist,
            "big5_averages": big5_avgs,
            "histogram": {
                "labels": hist_labels,
                "values": hist_counts.tolist()
            },
            "scatter": scatter_data,
            "stats": {
                "std_dev": round(std_dev, 3),
                "min": round(r_min, 2),
                "max": round(r_max, 2),
                "verdict": verdict,
                "verdict_msg": verdict_msg,
                "verdict_color": verdict_color
            },
            "raw_data": raw_table
        }

    except Exception as e:
        print(f"❌ Error Analytics: {e}")
        return {"error": str(e)}