# /pages/results.py

import streamlit as st
import os
import pandas as pd
import time
import threading
import json
import numpy as np # Importante para detectar tipos

from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.persistence import insert_survey_response
from utils.scales import INIT_PAGE
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# ==========================================================
# HELPER: SANITIZAR DATOS (Clave para evitar errores de DB)
# ==========================================================
def sanitize_dict(d):
    """
    Convierte tipos de NumPy (int64, float32) a tipos nativos de Python (int, float).
    Esto es crucial para que JSON y SQL no fallen.
    """
    new_d = {}
    for k, v in d.items():
        if isinstance(v, (np.integer, np.int64, np.int32)):
            new_d[k] = int(v)
        elif isinstance(v, (np.floating, np.float64, np.float32)):
            new_d[k] = float(v)
        elif isinstance(v, dict):
            new_d[k] = sanitize_dict(v)
        else:
            new_d[k] = v
    return new_d

# ==========================================================
# FUNCIÓN WORKER (Background)
# ==========================================================
def task_save_background(responses, scores, model_output):
    """
    Ejecuta la inserción en BD en un hilo aparte.
    """
    print("🔄 [Background] Hilo iniciado. Preparando inserción...")
    try:
        start_t = time.time()
        
        # Intentamos insertar
        insert_survey_response(
            responses=responses,
            scores=scores,
            model_output=model_output
        )
        
        duration = time.time() - start_t
        print(f"✅ [Background] Guardado exitoso en BDD en {duration:.4f}s")
        
    except Exception as e:
        # Este print es vital: aparecerá en tu terminal de VSCode/Servidor
        print(f"❌ [Background] FATAL ERROR guardando en DB: {e}")
        # Tip: Imprime los datos para ver si algo viene mal
        print(f"   Datos: {model_output}")

# ==========================================================
# EVIDENTLY REPORT
# ==========================================================
def generate_evidently_report():
    if not os.path.exists("training_baseline.csv") or not os.path.exists("production_predictions.csv"):
        st.error("❌ Faltan archivos de datos para el reporte.")
        return

    if os.path.exists("evidently_phishing_report.html"):
        st.info("📄 Usando reporte existente")
        return

    baseline = pd.read_csv("training_baseline.csv")
    production = pd.read_csv("production_predictions.csv")

    # Solo las features que usa el modelo nuevo
    FEATURES = [
        'Demo_Tamano_Org', 'Demo_Rol_Trabajo', 'Big5_Apertura',
        'Demo_Horas', 'Phish_Riesgo_Percibido', 'Fatiga_Global_Score'
    ]

    # Filtrar columnas si existen en el CSV, si no, manejar error
    try:
        baseline = baseline[FEATURES]
        production = production[FEATURES]
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=baseline, current_data=production)
        report.save_html("evidently_phishing_report.html")
    except KeyError as e:
        st.error(f"Error generando reporte: Falta columna {e}")

# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================
def page_results():
    st.markdown('<div class="bootstrap-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Análisis completado.")

    # 1️⃣ Obtener inputs y Scores
    responses = st.session_state.get("responses")    
    if not responses:
        st.error("⚠️ No hay respuestas registradas. Vuelva al inicio.")
        if st.button("Ir al Inicio"):
            st.session_state.page = INIT_PAGE
            st.rerun()
        return

    if st.session_state.get("scores") is None:
        scores = compute_scores(responses)
        st.session_state.scores = scores
    else:
        scores = st.session_state.scores

    # 2️⃣ Predicción
    if st.session_state.get("prediction") is None:
        try:
            # Preparamos features (Tu función arreglada de 6 vars)
            model_features = prepare_features(scores, responses)
            
            # Llamada al API
            st.session_state.prediction = predict(model_features)
            
        except Exception as e:
            st.error(f"Error conectando con el motor de IA: {e}")
            return

    result = st.session_state.prediction
    # Forzamos float nativo por seguridad
    probability = float(result.get("probability", 0.0))

    # 3️⃣ Lógica de Riesgo (Ajustada a tu modelo)
    if probability < 0.33:
        risk_level = "BAJO"
        msg_color = "success"
    elif probability < 0.40:
        risk_level = "MEDIO"
        msg_color = "warning"
    else:
        risk_level = "ALTO"
        msg_color = "error"

    # =================================================
    # 🔥 LOGICA FIRE AND FORGET (MEJORADA)
    # =================================================
    if not st.session_state.get("logged"):
        
        # A. Preparar datos limpios (Sin NumPy)
        clean_responses = sanitize_dict(responses)
        clean_scores = sanitize_dict(scores)
        clean_output = {
            "probability": probability,
            "risk_level": risk_level
        }
        
        # B. Lanzar Hilo
        # Usamos threading para no bloquear al usuario
        db_thread = threading.Thread(
            target=task_save_background, 
            args=(clean_responses, clean_scores, clean_output)
        )
        db_thread.start()
        
        # C. Marcar como logueado
        st.session_state.logged = True
        
        # D. Feedback visual sutil (Toast si es versión nueva, o info pequeña)
        try:
            st.toast("✅ Resultados calculados. Guardando registro anónimo...", icon="☁️")
        except AttributeError:
            st.info("☁️ Guardando registro anónimo en segundo plano...")

    # =================================================
    # 5️⃣ Mostrar resultado VISUAL
    # =================================================
    prob_pct = probability * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Probabilidad de Phishing:", f"{prob_pct:.1f}%")
    with col2:
        if msg_color == "success":
            st.success(f"Nivel de Riesgo: **{risk_level}**")
        elif msg_color == "warning":
            st.warning(f"Nivel de Riesgo: **{risk_level}**")
        else:
            st.error(f"Nivel de Riesgo: **{risk_level}**")
        
    st.markdown('</div>', unsafe_allow_html=True) 

    # =========================
    # Reinicio
    # =========================
    if st.button("🔄 Reiniciar evaluación"):
        keys_to_clear = ["page", "responses", "scores", "prediction", "logged"]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state.page = INIT_PAGE
        st.rerun()