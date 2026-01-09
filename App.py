import streamlit as st

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
#from pages.pages_likert import (
#    page_big5_extraversion,
#    page_big5_amabilidad,
#    page_big5_responsabilidad,
#    page_big5_neuroticismo,
#    page_big5_apertura,
#    page_phish_actitud_riesgo,
#    page_phish_awareness,
#    page_phish_riesgo_percibido,
#    page_phish_autoeficacia,
#    page_phish_susceptibilidad,
#    page_fatiga_emocional,
#    page_fatiga_cinismo,
#    page_fatiga_abandono
#)

from pages.pages_likert import (
    page_big5_responsabilidad,
    page_big5_apertura,
    page_phish_riesgo_percibido,
    page_fatiga_emocional,
    page_fatiga_cinismo,
    page_fatiga_abandono
)

from pages.demographics import page_demographics
from pages.results import page_results

# =========================
# Enrutador de páginas
# =========================
# PAGES = {
#    1: page_big5_extraversion,
#    2: page_big5_amabilidad,
#    3: page_big5_responsabilidad,
#    4: page_big5_neuroticismo,
#    5: page_big5_apertura,
#    6: page_phish_actitud_riesgo,
#    7: page_phish_awareness,
#    8: page_phish_riesgo_percibido,
#    9: page_phish_autoeficacia,
#    10: page_phish_susceptibilidad,
#    11: page_fatiga_emocional,
#    12: page_fatiga_cinismo,
#    13: page_fatiga_abandono,
#    14: page_demographics,
#    99: page_results
# }

PAGESAUX = {
    1: page_big5_responsabilidad,
    2: page_big5_apertura,
    3: page_phish_riesgo_percibido,
    4: page_fatiga_emocional,
    5: page_fatiga_cinismo,
    6: page_fatiga_abandono,
    7: page_demographics,
    99: page_results
}

# =========================
# Render de la página actual
# =========================
current_page = st.session_state.page

if current_page in PAGESAUX:
    PAGESAUX[current_page]()
else:
    st.error("Página no válida. Reiniciando encuesta.")
    st.session_state.page = 1
    st.rerun()