import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv

# --- DICCIONARIOS DE MAPEO (Según tu especificación) ---
MAP_PAIS = {1: 'Chile', 2: 'Colombia', 3: 'Honduras', 4: 'México', 5: 'Panamá'}
MAP_TORG = {1: 'Pública', 2: 'Privada', 3: 'Sin fines de Lucro', 4: 'Otras'}
MAP_TIND = {
    1: 'Agricultura', 2: 'Bancos o Financiera', 3: 'Seguros', 4: 'Tecnología',
    5: 'Marketing', 6: 'Transporte', 7: 'Salud', 8: 'AFP', 9: 'Sector Público',
    10: 'Energía', 11: 'Minería', 12: 'Oil & Gas', 13: 'Retail', 14: 'Educación',
    15: 'Consultoría', 16: 'Construcción', 17: 'Manufactura', 19: 'Otras'
}
MAP_NCOL = {
    1: '100 o menos', 2: '100-500', 3: '500-1000', 4: '1.000-3.000',
    5: '3.000-10.000', 6: '10.000-50.000', 7: '> 50.000'
}
MAP_TROL = {1: 'Liderazgo', 2: 'Supervisión', 3: 'Administrativo/Analista', 4: 'Otra'}
MAP_GEN = {1: 'Masculino', 2: 'Femenino', 3: 'No Binario'}
MAP_NEDU = {1: 'Primaria', 2: 'Pregrado', 3: 'Diplomado', 4: 'Magister', 5: 'Doctorado'}
MAP_NGEN = {1: 'Tradicionalistas', 2: 'Baby Boomers', 3: 'Gen X', 4: 'Millennials', 5: 'Gen Z'}
MAP_HOR = {1: '< 2h', 2: '2-5h', 3: '5-8h', 4: '8-10h', 5: '> 10h'}

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
        # Incluimos Scores, todas las preguntas respondidas con escala Likert
        target_cols = [
            "probability", "Big5_Apertura", "Big5_Responsabilidad", 
            "Big5_Extraversion", "Big5_Amabilidad", "Big5_Neuroticismo",
            "Phish_Actitud_Riesgo", "Phish_Awareness", "Phish_Riesgo_Percibido",
            "Phish_Autoeficacia", "Phish_Susceptibilidad", "Fatiga_Global_Score"  
        ]

        # Asegurar que existan y sean números (rellenar con 0 si faltan)
        for col in target_cols:
            if col not in df.columns:
                df[col] = 0.0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Columns for Demographic Analysis
        demo_cols = [
            "Demo_Pais", "Demo_Tipo_Organizacion", "Demo_Industria", 
            "Demo_Tamano_Org", "Demo_Rol_Trabajo", "Demo_Generacion_Edad", 
            "Demo_Genero", "Demo_Nivel_Educacion", "Demo_Horas"
        ]
        
        # Ensure demo cols exist
        for col in demo_cols:
            if col not in df.columns:
                df[col] = 0 # Default invalid

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
        # Enviamos todas las columnas numéricas + risk_level + Demografia
        # Convertimos a diccionario orientado a registros
        scatter_payload = df[target_cols + demo_cols + ["risk_level"]].to_dict(orient="records")

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