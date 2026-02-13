import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# --- NUEVO: Importar Mongo aquí ---
from pymongo import MongoClient

# Imports propios
from utils.scoring import compute_scores
from utils.probability import prepare_features, predict_model, load_local_model
from utils.persistence import save_survey_response
from utils.analytics import get_dashboard_stats

load_dotenv()

# Variable global para la base de datos (Igual que en FraudRisk)
db_collection = None

# --- CONFIGURACIÓN DE INICIO (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_collection
    
    # 1. Cargar Modelo Local
    print("🔄 Start-up: Cargando modelo de IA...")
    load_local_model()
    
    # 2. Conectar a MongoDB (Solo una vez)
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        try:
            # .strip() elimina espacios en blanco invisibles al copiar/pegar
            client = MongoClient(mongo_uri.strip()) 
            db = client["PhishingDetectorDB"]
            db_collection = db["susceptibilidad"]
            # Probamos conexión rápida para ver si falla aquí
            client.admin.command('ping')
            print("✅ Start-up: Conexión a MongoDB EXITOSA.")
        except Exception as e:
            print(f"⚠️ Start-up: Error conectando a MongoDB: {e}")
    else:
        print("⚠️ Advertencia: No hay MONGO_URI en .env")

    yield
    print("🛑 Shut-down: Apagando servidor.")

app = FastAPI(lifespan=lifespan)

# ... (Las clases BaseModel SurveyResponses y DashboardAuth siguen igual) ...
class SurveyResponses(BaseModel):
    responses: dict

class DashboardAuth(BaseModel):
    password: str

# ... (Rutas get /, get /questions.json siguen igual) ...
@app.get("/", response_class=HTMLResponse)
async def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: No se encuentra index.html</h1>"

@app.get("/static/questions.json")
async def get_questions_json():
    file_path = "questions.json"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    return {"error": "Archivo questions.json no encontrado"}


# ==========================================
# RUTA DE PROCESAMIENTO (MODIFICADA)
# ==========================================
@app.post("/submit")
async def submit_survey(data: SurveyResponses):
    raw_responses = data.responses
    print(f"📩 Recibidas {len(raw_responses)} respuestas.")

    # A. CALCULAR SCORES
    scores = compute_scores(raw_responses)
    
    # B. PREDECIR
    features_df = prepare_features(scores, raw_responses)
    model_output = predict_model(features_df)
    
    # C. GUARDAR EN MONGO (Usando la variable global)
    # ---------------------------------------------------------
    # Pasamos 'db_collection' que creamos al inicio
    save_success = save_survey_response(db_collection, raw_responses, scores, model_output)
    # ---------------------------------------------------------
    
    status_msg = "Datos guardados." if save_success else "Error guardando DB."

    final_record = {
        "responses": raw_responses,
        "scores": scores,
        "model_output": model_output,
        "saved_to_db": save_success
    }

    return {
        "status": "success", 
        "message": f"Análisis completado. {status_msg}",
        "final_record": final_record 
    }
    
# 2. RESTAURA ESTE ENDPOINT QUE FALTA:
@app.post("/analyze")
async def analyze_survey(data: SurveyResponses):
    try:
        raw_responses = data.responses
        print(f"📝 Recibidas {len(raw_responses)} respuestas.")

        # A. Calcular Puntajes
        scores = compute_scores(raw_responses)
        
        # B. Preparar Features para IA (Usando probability.py)
        features_df = prepare_features(scores, raw_responses)
        
        # C. Predecir con el Modelo
        model_output = predict_model(features_df)
        
        # D. Guardar en MongoDB (Usando la conexión global db_collection)
        save_success = save_survey_response(db_collection, raw_responses, scores, model_output)
        
        status_msg = "Datos guardados." if save_success else "Error guardando DB."

        # Estructura final para devolver al frontend
        final_record = {
            #"responses": raw_responses,
            "scores": scores,
            "model_output": model_output,
            "saved_to_db": save_success
        }

        return {
            "status": "success", 
            "message": f"Análisis completado. {status_msg}",
            "final_record": final_record 
        }

    except Exception as e:
        print(f"❌ Error en /analyze: {e}")
        return {"status": "error", "message": str(e)}



# ... (existing imports)

@app.post("/verify-dashboard")
async def verify_dashboard(data: DashboardAuth):
    stored_password = os.getenv("DASHBOARD_PASS")
    # Limpiamos el password guardado por si tiene comillas o espacios en el .env
    if stored_password:
        stored_password = stored_password.strip().strip('"').strip("'")
    
    # Limpiamos la contraseña ingresada por si el usuario incluyó espacios al copiar/pegar
    entered_password = data.password.strip()
    
    # Registro para depuración
    is_valid = (entered_password == stored_password)
    print(f"🔐 Intento de login al dashboard: {'EXITOSO' if is_valid else 'FALLIDO'}")
    
    if is_valid:
        return {"valid": True, "redirect_url": "/dashboard"} 
    else:
        return {"valid": False}



@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard():
    if os.path.exists("dashboard.html"):
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: dashboard.html no encontrado</h1>"

# ⚠️ ESTA ES LA RUTA QUE ARREGLA EL ERROR 404
@app.get("/dashboard-data")
async def dashboard_data():
    """
    El frontend llama a '/dashboard-data'. 
    Esta función busca los datos usando analytics.py
    """
    stats = get_dashboard_stats()
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)