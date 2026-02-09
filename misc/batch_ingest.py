import pandas as pd
import os
import sys

# ==============================================================================
# BLOQUE DE AJUSTE DE RUTAS (AGREGAR ESTO AL INICIO)
# ==============================================================================
# 1. Obtener la ruta absoluta de la carpeta donde está este script (misc)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Obtener la ruta raíz del proyecto (un nivel arriba de misc)
project_root = os.path.abspath(os.path.join(current_script_dir, '..'))

# 3. Agregar la raíz al 'sys.path' para poder importar 'utils'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 4. CAMBIAR EL DIRECTORIO DE TRABAJO A LA RAÍZ
# Esto es vital: hace que cuando los otros scripts busquen "questions.json" 
# o ".env", los encuentren en la raíz y no busquen en 'misc'.
os.chdir(project_root)
# ==============================================================================

from dotenv import load_dotenv
from pymongo import MongoClient
import time

# Importamos tus módulos existentes
from utils.scoring import compute_scores
from utils.probability import prepare_features, predict_model, load_local_model
from utils.persistence import save_survey_response

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN ---
INPUT_FILE = "phishing_clean.xlsx"  # Tu archivo de datos
MONGO_URI = os.getenv("MONGO_URI")

# Mapeo de tus columnas abreviadas a las que espera el sistema (questions.json)
# Ajusta esto según lo que signifique cada columna de tu dataset
COLUMN_MAPPING = {
    "PAIS": "Demo_Pais",
    "TORG": "Demo_Tipo_Organizacion",
    "TIND": "Demo_Industria",
    "NCOL": "Demo_Tamano_Org",  # Asumo que es Número Colaboradores
    "TROL": "Demo_Rol_Trabajo",
    "NGEN": "Demo_Generacion_Edad",
    "GEN":  "Demo_Genero",
    "NEDU": "Demo_Nivel_Educacion",
    "HOR":  "Demo_Horas"
}

def run_batch_process():
    print("🚀 Iniciando procesamiento masivo...")
    
    # 1. Conexión a Base de Datos
    if not MONGO_URI:
        print("❌ Error: Falta MONGO_URI en .env")
        return

    client = MongoClient(MONGO_URI)
    db = client["PhishingDetectorDB"]
    collection = db["susceptibilidad"]
    
    # 2. Cargar Modelo de IA (Solo una vez)
    print("🧠 Cargando modelo de IA...")
    model = load_local_model()
    if not model:
        print("❌ Error: No se pudo cargar el modelo phishing_model.pkl")
        return

    # 3. Leer el Dataset
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: No encuentro el archivo {INPUT_FILE}")
        return
    
    # Leemos el CSV (o Excel si prefieres pd.read_excel)
    df = pd.read_csv(INPUT_FILE)
    print(f"📂 Dataset cargado: {len(df)} filas encontradas.")

    # 4. Iterar y Procesar
    success_count = 0
    errors = 0

    for index, row in df.iterrows():
        try:
            # A. Convertir la fila a diccionario
            raw_data = row.to_dict()
            
            # B. Renombrar claves (Mapeo de Header Corto -> Header Sistema)
            # Esto crea un diccionario con claves como "Demo_Pais" en vez de "PAIS"
            # Las preguntas EX01, AM01, etc., se quedan igual.
            clean_responses = {}
            for k, v in raw_data.items():
                new_key = COLUMN_MAPPING.get(k, k) # Si está en el mapa lo cambia, si no, deja el original
                clean_responses[new_key] = v

            # C. Calcular Scores (Usa scoring.py)
            scores = compute_scores(clean_responses)

            # D. Prepara Features para IA (Usa probability.py)
            features_df = prepare_features(scores, clean_responses)
            
            # E. Predecir (Usa probability.py)
            if features_df is not None:
                model_output = predict_model(features_df)
            else:
                model_output = {"probability": 0, "risk_level": "Error Calc"}

            # F. Guardar en MongoDB (Usa persistence.py)
            # Nota: save_survey_response genera su propio ID y Timestamp
            saved = save_survey_response(collection, clean_responses, scores, model_output)
            
            if saved:
                success_count += 1
                # Opcional: imprimir progreso cada 10 filas
                if success_count % 10 == 0:
                    print(f"   ✅ Procesadas {success_count} filas...")
            else:
                errors += 1

        except Exception as e:
            print(f"   ⚠️ Error en fila {index}: {e}")
            errors += 1

    print("-" * 30)
    print(f"🏁 Proceso Finalizado.")
    print(f"✅ Éxito: {success_count}")
    print(f"❌ Errores: {errors}")

if __name__ == "__main__":
    run_batch_process()