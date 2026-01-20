import streamlit as st
import threading
import requests
import json
from utils.style import load_css
from utils.scales import INIT_PAGE
from utils.databricks import get_endpoint_url # Importamos solo para obtener la URL

# =========================
# Configuración básica
# =========================
st.set_page_config(
    page_title="Detector de Susceptibilidad a Phishing",
    layout="centered"
)

# =========================
# Lógica de "Despertador" (Wake Up) Seguro
# =========================

def wake_up_worker(url, token):
    """
    Esta función se ejecuta en un hilo separado.
    Recibe la URL y el Token directamente, por lo que NO toca st.secrets
    y no genera el error de ScriptRunContext.
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # Datos basura mínimos para despertar al modelo
        dummy_payload = {
            "dataframe_records": [{
                "Demo_Tamano_Org": 1,
                "Demo_Rol_Trabajo": 1,
                "Big5_Apertura": 0.5,
                "Demo_Horas": 1.0,
                "Phish_Riesgo_Percibido": 0.5,
                "Fatiga_Global_Score": 0.5
            }]
        }
        print(f"⏰ (Thread) Enviando señal de despertador a: {url}")
        requests.post(url, headers=headers, json=dummy_payload, timeout=5)
        print("✅ (Thread) Señal enviada.")
    except Exception as e:
        print(f"⚠️ (Thread) El despertador falló silenciosamente: {e}")

# =========================
# Inicio de la App
# =========================

load_css() 

st.title("🎣 Detector de Susceptibilidad a Phishing")
st.caption("Basado en personalidad, actitudes y fatiga digital")

# =========================
# Inicialización de estado y Thread
# =========================
if "page" not in st.session_state:
    st.session_state.page = INIT_PAGE

if "responses" not in st.session_state:
    st.session_state.responses = {}
    
if "scores" not in st.session_state:
    st.session_state.scores = None

if "prediction" not in st.session_state:
    st.session_state.prediction = None

# AQUÍ ESTÁ EL TRUCO: Solo lanzamos el hilo una vez por sesión
if "waked_up" not in st.session_state:
    
    # 1. Obtenemos las credenciales AQUI (en el hilo principal seguro)
    try:
        if "DATABRICKS_TOKEN" in st.secrets:
            token_safe = st.secrets["DATABRICKS_TOKEN"]
            # Usamos la función auxiliar para armar la URL, pero lo hacemos aquí
            url_safe = get_endpoint_url() 
            
            # 2. Lanzamos el hilo pasando los datos como argumentos
            # args=(url_safe, token_safe) evita que el hilo busque st.secrets
            t = threading.Thread(target=wake_up_worker, args=(url_safe, token_safe))
            t.start()
            
            st.session_state.waked_up = True
    except Exception as e:
        print(f"No se pudo iniciar el worker: {e}")

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
    st.session_state.page = INIT_PAGE
    st.rerun()