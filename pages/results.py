# /pages/results.py

import streamlit as st
import os
import pandas as pd
import time
import threading  # <--- IMPORTANTE: Para Fire and Forget
from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.persistence import insert_survey_response
from utils.scales import INIT_PAGE

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

# ==========================================================
# FUNCIÓN WORKER (Se ejecuta en segundo plano)
# ==========================================================
def task_save_background(responses, scores, probability, risk_level):
    """
    Esta función se ejecuta en un hilo separado.
    No puede escribir en la UI de Streamlit.
    """
    try:
        print("🔄 [Background] Iniciando guardado en Databricks...")
        start_t = time.time()
        
        model_out = {
            "probability": probability,
            "risk_level": risk_level
        }
        
        insert_survey_response(
            responses=responses,
            scores=scores,
            model_output=model_out
        )
        
        duration = time.time() - start_t
        print(f"✅ [Background] Guardado exitoso en {duration:.2f}s")
        
    except Exception as e:
        print(f"❌ [Background] Error guardando en DB: {e}")

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
    st.write("Este resultado se basa en sus respuestas y el análisis de IA.")

    # 1️⃣ Obtener inputs
    responses = st.session_state.get("responses")    
    if not responses:
        st.error("No hay respuestas registradas.")
        return

    if st.session_state.get("scores") is None:
        scores = compute_scores(responses)
        st.session_state.scores = scores
    else:
        scores = st.session_state.scores

    # 2️⃣ Preparar Features (Solo las 6 necesarias)
    try:
        model_features = prepare_features(scores, responses)
    except ValueError as e:
        st.error(f"Error preparando datos: {str(e)}")
        return
    
    # 3️⃣ Predicción (una sola vez)
    if st.session_state.get("prediction") is None:
        st.write("⏱️ Analizando patrones de comportamiento...")
        start_pred = time.time()
        
        try:
            st.session_state.prediction = predict(model_features)
        except Exception as e:
            st.error(f"Error de conexión con el modelo: {e}")
            return
        
        end_pred = time.time()
        seconds_pred = end_pred - start_pred
        st.sidebar.markdown("### ⏱️ Tiempos de Ejecución")
        st.sidebar.warning(f"🧠 Modelo IA: **{seconds_pred:.2f} seg**")

    result = st.session_state.prediction
    probability = result.get("probability", 0.0)

    # 4️⃣ Clasificación (Ajustada a la sensibilidad real del modelo)
    # Rango real observado: 0.29 (Mín) - 0.42 (Máx)
    
    probability_adj = float(probability)
    
    if probability_adj < 0.33:
        risk_level = "BAJO"
        msg_color = "success"
    elif probability_adj < 0.40:
        risk_level = "MEDIO"
        msg_color = "warning"
    else:
        risk_level = "ALTO"
        msg_color = "error"

    # =================================================
    # 📝 LOGICA FIRE AND FORGET
    # =================================================
    if not st.session_state.get("logged"):
        st.success("✅ Evaluación completada. (Guardando datos en segundo plano...)")
        
        # Lanzamos el hilo
        thread_args = (responses, scores, probability_adj, risk_level)
        db_thread = threading.Thread(target=task_save_background, args=thread_args)
        db_thread.start()
        
        st.session_state.logged = True

    # =================================================
    # 5️⃣ Mostrar resultado VISUAL
    # =================================================
    prob_pct = probability_adj * 100
    
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