# /pages/results.py

import streamlit as st
import os
import pandas as pd
import time
import threading  # <--- IMPORTANTE: Para Fire and Forget
from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.logging import log_prediction
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
    No puede escribir en la UI de Streamlit (st.write, st.error)
    porque el contexto de script principal ya habrá terminado para el usuario.
    """
    try:
        print("🔄 [Background] Iniciando guardado en Databricks...")
        start_t = time.time()
        
        # Preparamos el diccionario como lo espera tu función de persistencia
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
# EVIDENTLY (Tu código original)
# ==========================================================
def generate_evidently_report():
    if not os.path.exists("training_baseline.csv"):
        st.error("❌ No existe training_baseline.csv")
        return

    if not os.path.exists("production_predictions.csv"):
        st.error("❌ No hay datos de producción aún")
        return

    if os.path.exists("evidently_phishing_report.html"):
        st.info("📄 Usando reporte Evidently existente")
        return

    baseline = pd.read_csv("training_baseline.csv")
    production = pd.read_csv("production_predictions.csv")

    FEATURES = [
        'Demo_Tamano_Org', 'Demo_Rol_Trabajo', 'Big5_Apertura',
        'Demo_Horas', 'Phish_Riesgo_Percibido', 'Fatiga_Global_Score'
    ]

    baseline = baseline[FEATURES]
    production = production[FEATURES]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=baseline, current_data=production)
    report.save_html("evidently_phishing_report.html")

# ==========================================================
# PÁGINA PRINCIPAL
# ==========================================================
def page_results():
    st.markdown('<div class="bootstrap-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Este resultado se basa en sus respuestas.")

    # 1️⃣ Obtener scores
    responses = st.session_state.get("responses")    
    
    if not responses:
        st.error("No hay respuestas registradas.")
        return

    if st.session_state.get("scores") is None:
        scores = compute_scores(responses)
        st.session_state.scores = scores
    else:
        scores = st.session_state.scores

    try:
        model_features = prepare_features(scores, responses)
    except ValueError as e:
        st.error(str(e))
        return
    
    # 2️⃣ Predicción (una sola vez)
    if st.session_state.get("prediction") is None:
        st.write("⏱️ Iniciando predicción...")
        start_pred = time.time()
        
        st.session_state.prediction = predict(model_features)
        
        end_pred = time.time()
        seconds_pred = end_pred - start_pred
        st.sidebar.markdown("### ⏱️ Tiempos de Ejecución")
        st.sidebar.warning(f"🧠 Modelo IA: **{seconds_pred:.2f} seg**")

    result = st.session_state.prediction
    probability = result.get("probability")

    if probability is None:
        st.error("El modelo no devolvió una probabilidad válida.")
        return

    # 3️⃣ Clasificación
    probability_adj = probability 
    
    if probability_adj < 0.45:
        risk_level = "BAJO"
    elif probability_adj < 0.55:
        risk_level = "MEDIO"
    else:
        risk_level = "ALTO"

    # =================================================
    # 📝 LOGICA FIRE AND FORGET (NUEVA)
    # =================================================
    if not st.session_state.get("logged"):
        
        # 1. Mensaje inmediato al usuario
        st.success("✅ Evaluación completada. (Guardando datos en segundo plano...)")
        
        # 2. Preparamos los argumentos para el hilo
        # Pasamos copias de los datos, no el st.session_state completo por seguridad
        thread_args = (responses, scores, probability_adj, risk_level)
        
        # 3. Lanzamos el Hilo (Fire and Forget)
        db_thread = threading.Thread(target=task_save_background, args=thread_args)
        db_thread.start()
        
        # 4. Marcamos como logueado para que no se repita al recargar
        st.session_state.logged = True

    # =================================================
    # 4️⃣ Mostrar resultado VISUAL
    # =================================================

    prob_pct = probability_adj * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Su probabilidad de caer en Phishing es:", f"{prob_pct:.1f}%")
    with col2:
        if risk_level == "BAJO":
            st.success(f"Nivel de Riesgo: **{risk_level}**")
        elif risk_level == "MEDIO":
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