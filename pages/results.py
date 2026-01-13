import streamlit as st
import os
import pandas as pd

from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.logging import log_prediction

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
        "Big5_Responsabilidad",
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

    # Caso A: vienen desde appAlt (scores ya calculados)
    if st.session_state.get("scores") is not None:
        scores = st.session_state.scores

    # Caso B: vienen desde encuesta completa
    else:
        responses = st.session_state.get("responses")

        if not responses:
            st.error("No hay respuestas registradas.")
            return

        scores = compute_scores(responses)
        st.session_state.scores = scores


    scores = st.session_state.scores

    try:
        model_features = prepare_features(scores)
    except ValueError as e:
        st.error(str(e))
        return

    # =========================
    # 2️⃣ Predicción (una sola vez)
    # =========================
    if st.session_state.get("prediction") is None:
        st.session_state.prediction = predict(model_features)

    result = st.session_state.prediction
    prediction = result["prediction"]
    probability = result.get("probability")
    THRESHOLD = 0.60
    prediction = 1 if probability >= THRESHOLD else 0


    # Log solo una vez
    if not st.session_state.get("logged"):
        log_prediction(model_features, result)
        st.session_state.logged = True

    # =========================
    # 3️⃣ Mostrar resultado
    # =========================
    st.divider()

    if probability >= THRESHOLD:
        st.error("⚠️ Riesgo ALTO de susceptibilidad a phishing")
    else:
        st.success("✅ Riesgo BAJO de susceptibilidad a phishing")        
    st.caption(
    f"Umbral de riesgo configurado en {int(THRESHOLD*100)}%"
)



    if probability is not None:
        prob_pct = probability * 100

        st.markdown(
            f"""
            ### 📈 Resultado de la evaluación

            **Tienes un {prob_pct:.1f}% de probabilidad de caer en ataques de phishing.**
            """
        )

        st.progress(probability)
    else:
        st.caption("Probabilidad no disponible para este modelo.")


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
    if st.button("🔄 Reiniciar encuesta"):
        for k in ["page", "responses", "scores", "prediction", "logged"]:
            st.session_state.pop(k, None)
        st.session_state.page = 0
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


