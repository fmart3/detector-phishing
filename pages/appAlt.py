import streamlit as st

# =====================================================
# TODAS LAS PREGUNTAS DEL INSTRUMENTO
# =====================================================
# NOTA: Se eliminó 'FC04' porque no estaba en tu esquema SQL ni en scoring.py

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

    st.markdown("## ⚡ Modo Test – Respuestas Forzadas")
    st.caption("Esta herramienta simula el llenado completo de la encuesta para probar el pipeline (Scores -> Modelo -> SQL).")

    # Inicializar diccionario si no existe
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    col_btn, col_info = st.columns([1, 2])

    with col_btn:
        cargar = st.button("📥 Cargar Datos de Prueba", type="primary")

    if cargar:
        # 1. Limpiar estado previo para forzar recálculo en Results
        st.session_state.scores = None
        st.session_state.prediction = None
        st.session_state.responses = {} # Limpiar respuestas viejas
        
        r = st.session_state.responses

        # 2. Cargar Likert (Valor fijo = 3 para neutralidad)
        for q in LIKERT_QUESTIONS:
            r[q] = 3

        # 3. Cargar Demografía (Tipos de datos corregidos para databricks.py)
        # Aseguramos que coincidan con lo que espera prepare_features
        r.update({
            "Demo_Pais": 1,              # Chile (Int)
            "Demo_Tipo_Organizacion": 2, # Privada (Int)
            "Demo_Industria": 4,         # Tecnología (Int)
            "Demo_Tamano_Org": 3,        # 500–1000 (Int)
            "Demo_Rol_Trabajo": 3,       # Administrativo (Int) -> CRÍTICO para el modelo
            "Demo_Generacion_Edad": 4,   # Millennials (Int)
            "Demo_Genero": 1,            # Masculino (Int)
            "Demo_Nivel_Educacion": 4,   # Magíster (Int)
            "Demo_Horas": 2              # (Int)
        })

        st.success(f"✅ Se cargaron {len(r)} variables en memoria.")

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