import streamlit as st
import os
import pandas as pd
from utils.scoring import compute_scores
from utils.databricks import predict, prepare_features
from utils.logging import log_prediction

def page_results():

    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Este resultado se basa en sus respuestas.")

    responses = st.session_state.get("responses")

    if not responses:
        st.error("No hay respuestas registradas.")
        return

    # =========================
    # 1️⃣ Calcular scores (una sola vez)
    # =========================
    if st.session_state.get("scores") is None:
        st.session_state.scores = compute_scores(responses)

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

    result = predict(model_features)
    log_prediction(model_features, result) # Log para Evidently AI
    
    st.write("📂 Directorio actual:", os.getcwd())
    st.write("📄 Archivos en este directorio:", os.listdir("."))

    if os.path.exists("production_predictions.csv"):
        st.success("✅ CSV encontrado")
        st.dataframe(pd.read_csv("production_predictions.csv").tail())
    else:
        st.error("❌ CSV NO encontrado")
    
    prediction = result["prediction"]
    probability = result.get("probability")  # puede ser None


    # =========================
    # 3️⃣ Mostrar resultado
    # =========================
    st.divider()

    if prediction == 1:
        st.error("⚠️ Riesgo ALTO de susceptibilidad a phishing")
    else:
        st.success("✅ Riesgo BAJO de susceptibilidad a phishing")

    if probability is not None:
        st.markdown(
            f"### 📈 Susceptibilidad estimada: **{probability * 100:.1f}%**"
        )
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
        for k in ["page", "responses", "scores", "prediction"]:
            st.session_state.pop(k, None)
        st.session_state.page = 1
        st.experimental_rerun()
    
    with st.expander("🧾 Últimas predicciones registradas"):
        if os.path.exists("production_predictions.csv"):
            st.dataframe(pd.read_csv("production_predictions.csv").tail(10))
            with open("production_predictions.csv", "rb") as f:
                st.download_button(
                    label="📥 Descargar predicciones",
                    data=f,
                    file_name="production_predictions.csv",
                    mime="text/csv"
                )
