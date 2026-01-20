# /pages/results.py

import streamlit as st
import os
import pandas as pd
import time
from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.logging import log_prediction
from utils.persistence import insert_survey_response
from utils.scales import INIT_PAGE

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

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
        'Demo_Tamano_Org',
        'Demo_Rol_Trabajo',
        'Big5_Apertura',
        'Demo_Horas',
        'Phish_Riesgo_Percibido',
        'Fatiga_Global_Score'
    ]

    baseline = baseline[FEATURES]
    production = production[FEATURES]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=baseline, current_data=production)
    report.save_html("evidently_phishing_report.html")

def page_results():
    st.markdown('<div class="bootstrap-card">', unsafe_allow_html=True)
    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Este resultado se basa en sus respuestas.")

    # =========================
    # 1️⃣ Obtener scores
    # =========================

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
    
    # =========================
    # 2️⃣ Predicción (una sola vez)
    # =========================
    if st.session_state.get("prediction") is None:
        st.write("⏱️ Iniciando predicción...")
        start_pred = time.time()
        
        st.session_state.prediction = predict(model_features)
        
        end_pred = time.time()    # <--- FIN CRONÓMETRO PREDICCIÓN
        seconds_pred = end_pred - start_pred
        st.sidebar.markdown("### ⏱️ Tiempos de Ejecución")
        st.sidebar.warning(f"🧠 Modelo IA: **{seconds_pred:.2f} seg**")

    result = st.session_state.prediction
    probability = result.get("probability")

    if probability is None:
        st.error("El modelo no devolvió una probabilidad válida.")
        return

    # =========================
    # 3️⃣ Clasificación por niveles (NO binaria)
    # =========================
    
    probability_adj = probability 
    
    if probability_adj < 0.45:
        risk_level = "BAJO"
    elif probability_adj < 0.55:
        risk_level = "MEDIO"
    else:
        risk_level = "ALTO"

    # =================================================
    # 📝 LOGICA DE GUARDADO (OPTIMIZADA)
    # =================================================
    if not st.session_state.get("logged"):
        
        # Creamos un placeholder vacío PRIMERO
        status_placeholder = st.empty()
        
        # Usamos el status DENTRO del placeholder
        with status_placeholder.status("🔄 Procesando y guardando...", expanded=True) as status:
            
            st.write("☁️ Conectando con Base de Datos...")
            start_sql = time.time()
            
            # Llamada a la función de persistencia
            insert_survey_response(
                responses=responses,
                scores=scores,
                model_output={
                    "probability": probability_adj,
                    "risk_level": risk_level
                }
            )
            
            end_sql = time.time()
            seconds_sql = end_sql - start_sql
            
            # Mostramos info en sidebar (opcional, pero útil)
            st.sidebar.info(f"💾 Guardado DB: **{seconds_sql:.2f} s**")
            
            # Marcamos como logueado para que no se repita
            st.session_state.logged = True
            
            # Actualizamos el estado visual a Éxito
            status.update(label="✅ ¡Evaluación guardada con éxito!", state="complete", expanded=False)
            
            # Pequeña pausa para que el usuario vea el check verde antes de que desaparezca
            time.sleep(1.5)
        
        # (Opcional) Si quieres que desaparezca la caja de status por completo:
        status_placeholder.empty()

    # =========================
    # 4️⃣ Mostrar resultado
    # =========================
    #st.divider()

    prob_pct = probability_adj * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Su probabilidad de caer en Phishing es:", f"{prob_pct:.1f}%")
    with col2:
        # Usamos colores de streamlit basados en el nivel
        if risk_level == "BAJO":
            st.success(f"Nivel de Riesgo: **{risk_level}**")
        elif risk_level == "MEDIO":
            st.warning(f"Nivel de Riesgo: **{risk_level}**")
        else:
            st.error(f"Nivel de Riesgo: **{risk_level}**")
        
    st.markdown('</div>', unsafe_allow_html=True) # CIERRE CARD

    # =========================
    # Debug / académico
    # =========================
    with st.expander("🔍 Ver scores calculados"):
        st.json(scores)

    with st.expander("📦 Respuesta cruda del modelo"):
        st.json(result)

    # =========================
    # Reinicio
    # =========================
    #st.divider()
    if st.button("🔄 Reiniciar evaluación"):
        # 1. Limpiamos las variables de sesión
        keys_to_clear = ["page", "responses", "scores", "prediction", "logged"]
        for k in keys_to_clear:
            if k in st.session_state:
                del st.session_state[k]
        
        # 2. Establecemos la página de inicio (Generalmente es la 1)
        st.session_state.page = INIT_PAGE
        
        # 3. Forzamos la recarga con el comando nuevo
        st.rerun()

    # =========================
    # Evidently Report
    # =========================
    # st.divider()
    # if st.button("📈 Generar reporte de monitoreo"):
    #     generate_evidently_report()
    #     st.success("Reporte Evidently generado")

    # if os.path.exists("evidently_phishing_report.html"):
    #     st.components.v1.html(
    #         open("evidently_phishing_report.html").read(),
    #         height=800,
    #         scrolling=True
    #     )
