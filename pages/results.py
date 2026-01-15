# /pages/results.py

import streamlit as st
import os
import pandas as pd

from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.logging import log_prediction
from utils.persistence import insert_survey_response

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
        "Fatiga_Global_Score",
        "Phish_Susceptibilidad",
        "Big5_Apertura",
        "Phish_Riesgo_Percibido",
        "Demo_Rol_Trabajo",
        "Demo_Horas",
    ]

    baseline = baseline[FEATURES]
    production = production[FEATURES]

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=baseline, current_data=production)
    report.save_html("evidently_phishing_report.html")


def page_results():

    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Este resultado se basa en sus respuestas.")

    # =========================
    # 1️⃣ Obtener scores
    # =========================
    if st.session_state.get("scores") is not None:
        scores = st.session_state.scores
    else:
        responses = st.session_state.get("responses")

        if not responses:
            st.error("No hay respuestas registradas.")
            return

        scores = compute_scores(responses)
        st.session_state.scores = scores

    try:
        model_features = prepare_features(scores, responses)
    except ValueError as e:
        st.error(str(e))
        return
    
    with st.expander("🧪 DEBUG RESPONSES"):
        st.json(st.session_state.responses)


    # =========================
    # 2️⃣ Predicción (una sola vez)
    # =========================
    if st.session_state.get("prediction") is None:
        st.session_state.prediction = predict(model_features)

    result = st.session_state.prediction
    probability = result.get("probability")

    if probability is None:
        st.error("El modelo no devolvió una probabilidad válida.")
        return

    # =========================
    # 3️⃣ Clasificación por niveles (NO binaria)
    # =========================
    if probability < 0.45:
        risk_level = "BAJO"
        risk_color = "success"
        risk_msg = "🟢 Riesgo BAJO de susceptibilidad a phishing"
    elif probability < 0.55:
        risk_level = "MEDIO"
        risk_color = "warning"
        risk_msg = "🟡 Riesgo MEDIO de susceptibilidad a phishing"
    else:
        risk_level = "ALTO"
        risk_color = "error"
        risk_msg = "🔴 Riesgo ALTO de susceptibilidad a phishing"

    # Log solo una vez (guardamos score, no clase dura)
    if not st.session_state.get("logged"):

        responses = st.session_state.get("responses")

        if not responses:
            st.error("No hay respuestas para persistir.")
            return

        insert_survey_response(
            responses=responses,
            scores=scores,
            model_output={
                "probability": probability,
                "risk_level": risk_level
            }
        )

        log_prediction(
            model_features,
            {
                "risk_level": risk_level,
                "probability": probability
            }
        )

        st.session_state.logged = True

    # =========================
    # 4️⃣ Mostrar resultado
    # =========================
    st.divider()

    prob_pct = probability * 100

    st.markdown(
        f"""
        ### 📈 Resultado de la evaluación

        **Probabilidad estimada de susceptibilidad a phishing:**  
        **{prob_pct:.1f}%**
        """
    )

    st.progress(probability)

    if risk_color == "success":
        st.success(risk_msg)
    elif risk_color == "warning":
        st.warning(risk_msg)
    else:
        st.error(risk_msg)

    st.caption(
        "Este modelo funciona como un **score continuo de riesgo**, "
        "no como un clasificador binario estricto."
    )

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
    st.divider()
    if st.button("🔄 Reiniciar evaluación"):
        for k in ["page", "responses", "scores", "prediction", "logged"]:
            st.session_state.pop(k, None)
        st.session_state.page = 1
        st.experimental_rerun()

    st.divider()
    if st.button("📈 Generar reporte de monitoreo"):
        generate_evidently_report()
        st.success("Reporte Evidently generado")

    if os.path.exists("evidently_phishing_report.html"):
        st.components.v1.html(
            open("evidently_phishing_report.html").read(),
            height=800,
            scrolling=True
        )
