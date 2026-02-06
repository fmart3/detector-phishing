import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import json
from contextlib import asynccontextmanager

# Imports propios
from utils.scoring import compute_scores
# Nota: utils.databricks ahora contiene la lógica local que acabamos de escribir
from utils.databricks import prepare_features, predict_model, load_local_model
from utils.persistence import save_survey_response
from utils.analytics import get_dashboard_stats

# --- CONFIGURACIÓN DE INICIO ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar el modelo al iniciar la app
    print("🔄 Iniciando servidor... Intentando cargar modelo local.")
    load_local_model()
    yield
    print("🛑 Apagando servidor.")

app = FastAPI(lifespan=lifespan)

class SurveyResponses(BaseModel):
    responses: dict

class DashboardAuth(BaseModel):
    password: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: No se encuentra index.html</h1>"

@app.get("/questions.json")
async def get_questions_json():
    file_path = "questions.json"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/json")
    return {"error": "Archivo questions.json no encontrado"}

# ==========================================
# RUTA DE PROCESAMIENTO
# ==========================================
@app.post("/submit")
async def submit_survey(data: SurveyResponses):
    raw_responses = data.responses
    print(f"📩 1. Recibidas {len(raw_responses)} respuestas.")

    # A. CALCULAR SCORES
    scores = compute_scores(raw_responses)
    
    # B. PREDECIR CON MODELO LOCAL
    # Preparamos el DataFrame en lugar del JSON para API
    features_df = prepare_features(scores, raw_responses)
    
    # Obtenemos predicción directa del .pkl
    model_output = predict_model(features_df)
    
    print(f"🤖 Resultado Modelo Local: {model_output}")

    # C. GUARDAR EN MONGODB
    save_success = save_survey_response(raw_responses, scores, model_output)
    status_msg = "Datos guardados." if save_success else "Error guardando DB."

    # D. RESPONDER AL FRONTEND
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

# ==========================================
# RUTAS DEL DASHBOARD (ADMIN)
# ==========================================

@app.post("/verify-dashboard")
async def verify_dashboard(data: DashboardAuth):
    stored_pass = os.getenv("DASHBOARD_PASS")
    if not stored_pass:
        return {"valid": False, "error": "Contraseña no configurada en servidor"}
    
    if data.password == stored_pass:
        return {"valid": True, "redirect_url": "/dashboard"} 
    else:
        return {"valid": False}

@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard():
    if os.path.exists("dashboard.html"):
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: dashboard.html no encontrado</h1>"

@app.get("/api/dashboard-stats")
async def api_dashboard_stats():
    stats = get_dashboard_stats()
    return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)