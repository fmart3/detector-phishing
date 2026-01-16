import streamlit as st
import random

# =====================================================
# TODAS LAS PREGUNTAS DEL INSTRUMENTO
# =====================================================

LIKERT_QUESTIONS = [
    # Big Five
    "EX01","EX02","EX03","EX04","EX05", "EX06","EX07","EX08","EX09","EX10",
    "AM01","AM02","AM03","AM04","AM05", "AM06","AM07","AM08","AM09","AM10",
    "CO01","CO02","CO03","CO04","CO05", "CO06","CO07","CO08","CO09","CO10",
    "NE01","NE02","NE03","NE04","NE05", "NE06","NE07","NE08","NE09","NE10",
    "AE01","AE02","AE03","AE04","AE05", "AE06","AE07","AE08","AE09","AE10",

    # Phishing
    "ER01","ER02","ER03","ER04", "ER05","ER06","ER07","ER08","ER09","ER10",
    "AW01","AW02","AW03",
    "PR01","PR02","PR03",
    "CP01","CP02","CP03",
    "SU01","SU02","SU03","SU04",

    # Fatiga digital
    "FE01","FE02","FE03",
    "FC01","FC02","FC03","FC04",
    "DS01","DS02"
]

# =====================================================
# PAGE
# =====================================================

def page_app_alt():

    st.markdown("## ⚡ Modo Test – Respuestas Forzadas")
    st.caption("Todas las preguntas individuales = 3")

    if "responses" not in st.session_state:
        st.session_state.responses = {}

    col_btn, col_info = st.columns([1, 2])

    with col_btn:
        # Cambié el nombre del botón para reflejar que es aleatorio
        cargar = st.button("🎲 Generar Datos Random", type="primary")

    if cargar:
        # 1. Limpiar estado previo
        st.session_state.scores = None
        st.session_state.prediction = None
        st.session_state.responses = {} 
        
        r = st.session_state.responses

        # 2. Generar Respuestas Likert Aleatorias (1 a 5)
        for q in LIKERT_QUESTIONS:
            val = random.randint(1, 5) # <--- AQUÍ ESTÁ LA MAGIA
            r[q] = val

        # 3. Cargar Demografía 
        # Mantengo los demográficos fijos para que sea un perfil consistente,
        # pero 'Demo_Horas' sigue siendo INT como pediste.
        r.update({
            "Demo_Pais": 1,              # Chile
            "Demo_Tipo_Organizacion": 2, # Privada
            "Demo_Industria": 4,         # Tecnología
            "Demo_Tamano_Org": 3,        # 500–1000
            "Demo_Rol_Trabajo": 3,       # Administrativo
            "Demo_Generacion_Edad": 4,   # Millennials
            "Demo_Genero": 1,            # Masculino
            "Demo_Nivel_Educacion": 4,   # Magíster
            
            # Si quieres randomizar las horas también (entre 1 y 5), usa:
            # "Demo_Horas": random.randint(1, 5)
            "Demo_Horas": 3              # Dejamos 3 fijo por ahora (Entre 5 y 8 horas)
        })

        st.success(f"✅ Se generaron respuestas aleatorias para {len(LIKERT_QUESTIONS)} preguntas.")

    # =====================================================
    # VISUALIZACIÓN DE DATOS (DEBUG)
    # =====================================================
    st.divider()
    
    if st.session_state.responses:
        with st.expander("🔍 Ver datos generados (JSON)", expanded=True):
            st.json(st.session_state.responses)

        st.markdown("---")
        st.markdown("### 🚀 Ejecución del Pipeline")
        st.info("Presiona abajo para calcular los scores basados en estos números aleatorios y enviarlos a Databricks.")
        
        if st.button("Calcular, Predecir y Guardar >>"):
            st.session_state.page = 99
            st.rerun()
    else:
        st.warning("⚠️ Primero presiona 'Generar Datos Random'")
