import os
import sys

INPUT_FILE = "phishing_clean.xlsx"  

# ==============================================================================
# BLOQUE DE AJUSTE DE RUTAS (Mantiene compatibilidad con carpeta misc)
# ==============================================================================
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)
# ==============================================================================

import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
import openpyxl
import time

from utils.scoring import compute_scores
from utils.probability import prepare_features, predict_model, load_local_model
from utils.persistence import save_survey_response

load_dotenv()

# --- CONFIGURACIÓN ---
MONGO_URI = os.getenv("MONGO_URI")

# 1. MAPEO: De nombres cortos (Excel) a nombres del sistema
COLUMN_MAPPING = {
    "PAIS": "Demo_Pais",
    "TORG": "Demo_Tipo_Organizacion",
    "TIND": "Demo_Industria",
    "NCOL": "Demo_Tamano_Org",
    "TROL": "Demo_Rol_Trabajo",
    "NGEN": "Demo_Generacion_Edad",
    "GEN":  "Demo_Genero",
    "NEDU": "Demo_Nivel_Educacion",
    "HOR":  "Demo_Horas"
}

# 2. LISTA NEGRA: Columnas a ELIMINAR/IGNORAR
# Estas columnas no se guardarán en MongoDB ni se usarán para cálculos

def run_batch_process():
    print(f"🚀 Iniciando procesamiento masivo...")
    
    if not MONGO_URI:
        print("❌ Error: Falta MONGO_URI en .env")
        return

    client = MongoClient(MONGO_URI)
    db = client["PhishingDetectorDB"]
    collection = db["susceptibilidad"]
    
    print("🧠 Cargando modelo de IA...")
    model = load_local_model()
    if not model:
        return

    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: No encuentro el archivo {INPUT_FILE}")
        return
    
    print(f"📖 Leyendo archivo Excel: {INPUT_FILE} ...")
    try:
        df = pd.read_excel(INPUT_FILE) # <--- CAMBIO AQUÍ
    except Exception as e:
        print(f"❌ Error crítico al leer el Excel. Verifica que tengas 'openpyxl' instalado.")
        print(f"Detalle: {e}")
        return

    print(f"📂 Dataset cargado: {len(df)} filas.")

    success_count = 0
    errors = 0

    # 4. Iterar y Procesar
    for index, row in df.iterrows():
        try:
            raw_data = row.to_dict()
            clean_responses = {}

            # --- LIMPIEZA Y FILTRADO ---
            for k, v in raw_data.items():
                
                # B. Mapeo de nombres (si corresponde)
                new_key = COLUMN_MAPPING.get(k, k)
                
                # C. Guardamos el valor limpio
                clean_responses[new_key] = v

            # --- CÁLCULOS Y GUARDADO ---
            # Ahora 'clean_responses' YA NO TIENE NE11 NI VPH
            
            scores = compute_scores(clean_responses)
            features_df = prepare_features(scores, clean_responses)
            
            if features_df is not None:
                model_output = predict_model(features_df)
            else:
                model_output = {"probability": 0, "risk_level": "Error Calc"}

            saved = save_survey_response(collection, clean_responses, scores, model_output)
            
            if saved:
                success_count += 1
                if success_count % 10 == 0:
                    print(f"   ✅ Procesadas {success_count} filas...")
            else:
                errors += 1

        except Exception as e:
            print(f"   ⚠️ Error en fila {index}: {e}")
            errors += 1

    print("-" * 30)
    print(f"🏁 Finalizado. Éxitos: {success_count} | Errores: {errors}")

if __name__ == "__main__":
    run_batch_process()