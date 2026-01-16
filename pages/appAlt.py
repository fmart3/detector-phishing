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

    # Fatiga digital (Solo las definidas en Schema)
    "FE01","FE02","FE03",
    "FC01","FC02","FC03", "FC04",
    "DS01","DS02"
]

# =====================================================
# PAGE
# =====================================================

def page_app_alt():

    st.markdown("## ⚡Test Rápido – Respuestas Aleatorias")
    st.caption("Esta herramienta simula el llenado completo de la encuesta para probar el pipeline (Scores -> Modelo -> SQL).")

    # Inicializar diccionario si no existe
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    col_btn, col_info = st.columns([1, 2])

    with col_btn:
        cargar = st.button("📥 Cargar Datos Random", type="primary")

    if cargar:
        # 1. Limpiar estado previo
        st.session_state.scores = None
        st.session_state.prediction = None
        st.session_state.responses = {} 
        
        r = st.session_state.responses

        # 2. Cargar Likert Aleatorio (1 a 5)
        for q in LIKERT_QUESTIONS:
            r[q] = random.randint(1, 2)

        # 3. Cargar Demografía Aleatoria
        # Los rangos (randint) coinciden con el largo de tus diccionarios en demographics.py
        r.update({
            "Demo_Pais": random.randint(1, 5),              # 5 Países
            "Demo_Tipo_Organizacion": random.randint(1, 4), # 4 Tipos
            "Demo_Industria": random.randint(1, 18),        # 18 Industrias
            "Demo_Tamano_Org": random.randint(1, 5),        # 5 Rangos de tamaño
            "Demo_Rol_Trabajo": random.randint(1, 1),       # 4 Roles
            "Demo_Generacion_Edad": random.randint(1, 5),   # 5 Generaciones
            "Demo_Genero": random.randint(1, 4),            # 4 Opciones género
            "Demo_Nivel_Educacion": random.randint(1, 5),   # 5 Niveles
            "Demo_Horas": random.randint(1, 5)              # 5 Rangos de horas
        })

        st.success(f"✅ Se generaron {len(r)} variables con valores aleatorios.")

    # =====================================================
    # VISUALIZACIÓN DE DATOS (DEBUG)
    # =====================================================
    st.divider()
    
    if st.session_state.responses:
        with st.expander("🔍 Ver datos cargados en JSON (Payload)", expanded=True):
            st.json(st.session_state.responses)

        st.markdown("---")
        st.markdown("### 🚀 Ejecución del Pipeline")
        st.info("Al presionar el botón, se redirigirá a la página de Resultados (99), donde se calcularán los scores, se consultará a Databricks y se guardará en SQL.")
        
        if st.button("Calcular, Predecir y Guardar >>"):
            st.session_state.page = 99
            st.rerun()
    else:
        st.warning("⚠️ Primero presiona 'Cargar Datos de Prueba'")