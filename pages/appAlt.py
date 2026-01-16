import streamlit as st

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

    r = st.session_state.responses

    # =====================================================
    # 1️⃣ RESPUESTAS LIKERT (TODAS = 3)
    # =====================================================
    st.divider()
    st.markdown("### 📋 Respuestas del cuestionario")

    for q in LIKERT_QUESTIONS:
        r[q] = 3

    st.success(f"✅ {len(LIKERT_QUESTIONS)} preguntas cargadas con valor 3")

    # =====================================================
    # 2️⃣ DEMOGRAFÍA (VALORES VÁLIDOS)
    # =====================================================
    st.divider()
    st.markdown("### 👤 Demografía (codificada)")

    r.update({
        "Demo_Pais": 1,               # Chile
        "Demo_Tipo_Organizacion": 2,  # Privada
        "Demo_Industria": 4,          # Tecnología
        "Demo_Tamano_Org": 3,         # 500–1000
        "Demo_Rol_Trabajo": 1,        # Administrativo / Técnico
        "Demo_Generacion_Edad": 4,    # Millennials
        "Demo_Genero": 1,             # Masculino
        "Demo_Nivel_Educacion": 4,    # Magíster
        "Demo_Horas": 3               # 5–8 horas
    })

    st.success("✅ Demografía cargada")

    # =====================================================
    # DEBUG
    # =====================================================
    st.divider()
    with st.expander("🧪 DEBUG – responses"):
        st.json(r)

    # =====================================================
    # CONTROL
    # =====================================================
    if st.button("🚀 Ir a resultados"):
        st.session_state.page = 99
        st.rerun()
