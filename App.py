""""import streamlit as st

# =========================
# Configuración básica
# =========================
st.set_page_config(
    page_title="Detector de Susceptibilidad a Phishing",
    layout="centered"
)

st.title("🎣 Detector de Susceptibilidad a Phishing")
st.caption("Basado en personalidad, actitudes y fatiga digital")

# =========================
# Inicialización de estado
# =========================
if "page" not in st.session_state:
    st.session_state.page = 1

if "responses" not in st.session_state:
    st.session_state.responses = {}
    
if "scores" not in st.session_state:
    st.session_state.scores = None

if "prediction" not in st.session_state:
    st.session_state.prediction = None

# =========================
# Importación de páginas
# =========================
from pages.pages_likert import (
    page_big5_extraversion,
    page_big5_amabilidad,
    page_big5_responsabilidad,
    page_big5_neuroticismo,
    page_big5_apertura,
    page_phish_actitud_riesgo,
    page_phish_awareness,
    page_phish_riesgo_percibido,
    page_phish_autoeficacia,
    page_phish_susceptibilidad,
    page_fatiga_emocional,
    page_fatiga_cinismo,
    page_fatiga_abandono
)

from pages.demographics import page_demographics
from pages.results import page_results

# =========================
# Enrutador de páginas
# =========================
PAGES = {
    1: page_big5_extraversion,
    2: page_big5_amabilidad,
    3: page_big5_responsabilidad,
    4: page_big5_neuroticismo,
    5: page_big5_apertura,
    6: page_phish_actitud_riesgo,
    7: page_phish_awareness,
    8: page_phish_riesgo_percibido,
    9: page_phish_autoeficacia,
    10: page_phish_susceptibilidad,
    11: page_fatiga_emocional,
    12: page_fatiga_cinismo,
    13: page_fatiga_abandono,
    14: page_demographics,
    99: page_results
}

# =========================
# Render de la página actual
# =========================
current_page = st.session_state.page

if current_page in PAGES:
    PAGES[current_page]()
else:
    st.error("Página no válida. Reiniciando encuesta.")
    st.session_state.page = 1
    st.experimental_rerun()
    
"""""

# APP PRUEBA RAPIDA

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
)

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
        st.exception(e)
