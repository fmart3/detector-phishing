import streamlit as st
from utils.databricks import predict, prepare_features

st.set_page_config(
    page_title="Test conexión modelo Phishing",
    layout="centered"
)

st.title("🧪 Test rápido – Modelo Phishing")
st.caption("Ingreso manual de scores para validar conexión con Databricks")

st.divider()

st.subheader("📥 Ingreso de variables")

Fatiga_Global_Score = st.slider(
    "Fatiga Global Score",
    min_value=1.0,
    max_value=5.0,
    step=0.1
)

Big5_Responsabilidad = st.slider(
    "Big5 – Responsabilidad",
    min_value=1.0,
    max_value=5.0,
    step=0.1
)

Big5_Apertura = st.slider(
    "Big5 – Apertura",
    min_value=1.0,
    max_value=5.0,
    step=0.1
)

Demo_Generacion_Edad = st.selectbox(
    "Generación",
    options={
        "Tradicionalistas": 1,
        "Baby Boomers": 2,
        "Generación X": 3,
        "Millennials": 4,
        "Generación Z": 5
    }.items(),
    format_func=lambda x: x[0]
)[1]

Demo_Rol_Trabajo = st.selectbox(
    "Rol de trabajo",
    options={
        "Liderazgo": 1,
        "Supervisión": 2,
        "Profesional / Analista": 3,
        "Otro": 4
    }.items(),
    format_func=lambda x: x[0]
)[1]

Demo_Horas = st.selectbox(
    "Horas diarias frente al computador",
    options={
        "Menos de 2 horas": 1,
        "Entre 2 y 5 horas": 2,
        "Entre 5 y 8 horas": 3,
        "Entre 8 y 10 horas": 4,
        "Más de 10 horas": 5
    }.items(),
    format_func=lambda x: x[0]
)[1]

st.divider()

if st.button("🚀 Ejecutar predicción"):

    scores = {
        "Fatiga_Global_Score": Fatiga_Global_Score,
        "Big5_Responsabilidad": Big5_Responsabilidad,
        "Big5_Apertura": Big5_Apertura,
        "Demo_Generacion_Edad": Demo_Generacion_Edad,
        "Demo_Rol_Trabajo": Demo_Rol_Trabajo,
        "Demo_Horas": Demo_Horas
    }

    try:
        features = prepare_features(scores)
        result = predict(features)

        st.success("✅ Conexión exitosa con Databricks")

        st.subheader("📊 Resultado del modelo")

        if result["prediction"] == 1:
            st.error("⚠️ Riesgo ALTO de susceptibilidad a phishing")
        else:
            st.success("✅ Riesgo BAJO de susceptibilidad a phishing")

        with st.expander("🔎 Ver payload enviado"):
            st.json(features)

        with st.expander("📦 Respuesta completa del endpoint"):
            st.json(result)

    except Exception as e:
        st.error("❌ Error al ejecutar la predicción")
        st.write("Secrets disponibles:", list(st.secrets.keys()))
        st.exception(e)