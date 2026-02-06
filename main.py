import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os
import json

# Imports propios
from utils.scoring import compute_scores
from utils.databricks import prepare_features, predict_model
from utils.persistence import insert_response_sql
from utils.analytics import get_dashboard_stats

app = FastAPI()

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
    try:
        scores = compute_scores(raw_responses)
        print("✅ 2. Scores calculados.")
    except Exception as e:
        print(f"❌ Error en scores: {e}")
        scores = {}

    # B. LLAMAR AL MODELO
    try:
        model_payload = prepare_features(scores, raw_responses)
        model_output = predict_model(model_payload)
        print(f"✅ 3. Modelo respondió: {model_output['risk_level']}")
    except Exception as e:
        print(f"❌ Error llamando al modelo: {e}")
        model_output = {"probability": -1, "risk_level": "Error Backend"}

    # C. GUARDAR EN BASE DE DATOS (AHORA SÍ)
    # ---------------------------------------------------------
    save_success = insert_response_sql(raw_responses, scores, model_output)
    status_msg = "Datos guardados correctamente." if save_success else "Error guardando en base de datos."
    # ---------------------------------------------------------

    # D. RESPONDER AL FRONTEND
    # Construimos el objeto final para que el usuario vea sus resultados
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

# 1. Verificación de Contraseña (FALTABA ESTA RUTA)
@app.post("/verify-dashboard")
async def verify_dashboard(data: DashboardAuth):
    # Lee la contraseña del archivo .env
    stored_pass = os.getenv("DASHBOARD_PASS")
    
    if not stored_pass:
        return {"valid": False, "error": "Contraseña no configurada en servidor"}
    
    if data.password == stored_pass:
        # Redirigimos a la ruta interna del dashboard
        return {"valid": True, "redirect_url": "/dashboard"} 
    else:
        return {"valid": False}

# 2. Servir el HTML del Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard():
    if os.path.exists("dashboard.html"):
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Error: dashboard.html no encontrado</h1>"

# 3. API para obtener los datos (JSON)
@app.get("/api/stats")
async def get_stats():
    data = get_dashboard_stats()
    return data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)