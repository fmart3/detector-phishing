import streamlit as st
from utils.scoring import compute_scores
from utils.databricks import predict

def page_results():

    st.markdown("## 📊 Resultado de la Evaluación")
    st.write("Este resultado se basa en sus respuestas.")

    responses = st.session_state.get("responses", {})

    if not responses:
        st.error("No hay respuestas registradas.")
        return

    # =========================
    # 1️⃣ Calcular scores (una sola vez)
    # =========================
    if st.session_state.scores is None:
        st.session_state.scores = compute_scores(responses)

    scores = st.session_state.scores

    # =========================
    # 2️⃣ Predicción (una sola vez)
    # =========================
    if st.session_state.prediction is None:
        st.session_state.prediction = predict(scores)

    result = st.session_state.prediction
    prediction = result["prediction"]
    probability = result["probability"]

    # =========================
    # 3️⃣ Mostrar resultado
    # =========================
    st.divider()

    if prediction == 1:
        st.error("⚠️ Riesgo ALTO de susceptibilidad a phishing")
    else:
        st.success("✅ Riesgo BAJO de susceptibilidad a phishing")

    if probability is not None:
        st.caption(f"Probabilidad estimada de riesgo: **{probability:.2%}**")

    # =========================
    # Debug / académico
    # =========================
    with st.expander("🔍 Ver scores calculados"):
        st.json(scores)

    # =========================
    # Reinicio
    # =========================
    st.divider()
    if st.button("🔄 Reiniciar encuesta"):
        for k in ["page", "responses", "scores", "prediction"]:
            st.session_state.pop(k, None)
        st.session_state.page = 1
        st.experimental_rerun()
