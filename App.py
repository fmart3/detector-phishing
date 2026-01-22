import streamlit as st
import threading
import hmac
from utils.databricks import predict
from utils.scales import INIT_PAGE

# =========================
# Configuración básica
# =========================

st.set_page_config(
    page_title="Detector de Susceptibilidad a Phishing",
    layout="centered"

)
# Función silenciosa para despertar al modelo
def wake_up_model():
    try:
        # Enviamos datos basura solo para activar el servidor
        # No nos importa el resultado, solo que el servidor arranque
        dummy_data = {
            "Fatiga_Global_Score": 0, "Phish_Susceptibilidad": 0,
            "Big5_Apertura": 0, "Phish_Riesgo_Percibido": 0,
            "Demo_Rol_Trabajo": 0, "Demo_Horas": 0
            # ... asegúrate de incluir las columnas mínimas que pide tu modelo
        }
        print("⏰ Enviando señal de despertador a Databricks...")
        predict(dummy_data)
    except:
        pass # Si falla no importa, era solo para despertar
    
st.markdown("""
    <style>
        /* Oculta la lista de páginas en el sidebar */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        [theme]
        primaryColor = "#194485"  # El azul clásico de Bootstrap (Primary)
        backgroundColor = "#1e2f41" # Gris muy claro de fondo (tipo Bootstrap)
        secondaryBackgroundColor = "#000000" # Blanco para el sidebar y tarjetas
        textColor = "#ffffff" # Gris oscuro para texto
        font = "comic sans"

        [server]
        runOnSave = true

        [client]
        showSidebarNavigation = false
    </style>
""", unsafe_allow_html=True)

st.title("🎣 Detector de Susceptibilidad a Phishing")
st.caption("Basado en personalidad, actitudes y fatiga digital")

# =========================
# Inicialización de estado
# =========================

if "page" not in st.session_state:
    st.session_state.page = INIT_PAGE
    
if "responses" not in st.session_state:
    st.session_state.responses = {}

if "scores" not in st.session_state:
    st.session_state.scores = None
    
if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "waked_up" not in st.session_state:
    # Usamos un hilo (thread) para que NO congele la pantalla de inicio
    thread = threading.Thread(target=wake_up_model)
    thread.start()
    st.session_state.waked_up = True

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
from pages.appAlt import page_app_alt

# =========================
# Enrutador de páginas
# =========================

PAGES = {
    0: page_app_alt,
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
    
# ---------------------------------------------------------
# 🔐 ACCESO ADMINISTRADOR (En el Sidebar)
# ---------------------------------------------------------
st.sidebar.divider()
st.sidebar.markdown("### 🔧 Zona Admin")

# 1. Input de contraseña
password = st.sidebar.text_input("Contraseña de acceso", type="password")

# 2. Botón de validación
if st.sidebar.button("Ir al Dashboard"):
    
    # A. Recuperamos la contraseña real desde los secrets
    # Usamos .get() para evitar que la app explote si se te olvida poner el secreto
    admin_secret = st.secrets.get("DASHBOARD_PASS")

    if not admin_secret:
        st.sidebar.error("⚠️ Error: No se configuró la contraseña en secrets.toml")
    
    # B. Comparación Segura (Evita ataques de tiempo)
    # En lugar de (password == admin_secret), usamos hmac
    elif hmac.compare_digest(password, admin_secret):
        st.sidebar.success("Acceso concedido. Redirigiendo...")
        st.switch_page("pages/dashboard.py")
        
    # C. Contraseña Incorrecta
    else:
        st.sidebar.error("❌ Contraseña incorrecta")