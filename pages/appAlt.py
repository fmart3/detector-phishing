import streamlit as st
import random

# =====================================================
# IMPORTAR PREGUNTAS (Fuente Única de Verdad)
# =====================================================
from components.questions_likert import (
    BIG5_EXTRAVERSION, BIG5_AMABILIDAD, BIG5_RESPONSABILIDAD, 
    BIG5_NEUROTICISMO, BIG5_APERTURA,
    PHISH_ACTITUD_RIESGO, PHISH_AWARENESS, PHISH_RIESGO_PERCIBIDO, 
    PHISH_AUTOEFICACIA, PHISH_SUSCEPTIBILIDAD,
    FATIGA_EMOCIONAL, FATIGA_CINISMO, FATIGA_ABANDONO
)

# Agrupamos todas las listas importadas en una sola lista maestra
ALL_GROUPS = [
    BIG5_EXTRAVERSION, BIG5_AMABILIDAD, BIG5_RESPONSABILIDAD, 
    BIG5_NEUROTICISMO, BIG5_APERTURA,
    PHISH_ACTITUD_RIESGO, PHISH_AWARENESS, PHISH_RIESGO_PERCIBIDO, 
    PHISH_AUTOEFICACIA, PHISH_SUSCEPTIBILIDAD,
    FATIGA_EMOCIONAL, FATIGA_CINISMO, FATIGA_ABANDONO
]

# Generamos la lista de códigos dinámicamente: ["EX01", "EX02", ..., "DS02"]
LIKERT_QUESTIONS = [q["code"] for group in ALL_GROUPS for q in group]


# =====================================================
# PAGE APP ALT
# =====================================================

def page_app_alt():
    st.markdown("## ⚡ Simulador de Escenarios (Test Rápido)")
    st.caption("Define manualmente las variables clave para el modelo. El resto (relleno para SQL) será aleatorio.")

    # -----------------------------------------------------
    # 1. CONTROLES MANUALES (Inputs del Modelo)
    # -----------------------------------------------------
    
    st.subheader("🎛️ Configura tu Perfil de Prueba")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🏢 Datos Demográficos")
        
        input_tamano = st.selectbox(
            "Tamaño Organización",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1. Micro (1-10)", 
                2: "2. Pequeña (11-50)", 
                3: "3. Mediana (51-200)", 
                4: "4. Grande (201-500)", 
                5: "5. Muy Grande (500+)"
            }[x]
        )

        input_rol = st.selectbox(
            "Rol de Trabajo",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "1. Administrativo/Staff", 
                2: "2. Técnico/IT", 
                3: "3. Manager/Gerente", 
                4: "4. Ejecutivo/Directivo"
            }[x]
        )

        input_horas = st.selectbox(
            "Horas de Uso (Dispositivo)",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1. < 2 horas", 
                2: "2. 2-4 horas", 
                3: "3. 4-6 horas", 
                4: "4. 6-8 horas", 
                5: "5. > 8 horas"
            }[x]
        )

    with col2:
        st.markdown("##### 🧠 Scores Psicológicos")
        
        input_apertura = st.slider(
            "Big5 - Apertura (Openness)", 
            min_value=1.0, max_value=5.0, value=3.5, step=0.1,
            help="Qué tan abierta a nuevas experiencias es la persona."
        )
        
        input_riesgo = st.slider(
            "Riesgo Percibido", 
            min_value=1.0, max_value=5.0, value=3.0, step=0.1,
            help="Qué tanto riesgo cree el usuario que existe en internet."
        )
        
        input_fatiga = st.slider(
            "Fatiga Global", 
            min_value=1.0, max_value=5.0, value=2.5, step=0.1,
            help="Nivel de agotamiento digital."
        )

    st.divider()

    # -----------------------------------------------------
    # 2. BOTÓN DE ACCIÓN
    # -----------------------------------------------------
    
    if st.button("🚀 Simular Predicción con estos datos", type="primary"):
        
        # A. Inicializar/Limpiar estado
        st.session_state.scores = {}
        st.session_state.responses = {}
        st.session_state.prediction = None
        
        r = st.session_state.responses
        s = st.session_state.scores 

        # B. Generar Relleno Aleatorio (Usando la lista dinámica LIKERT_QUESTIONS)
        # ---------------------------------------------------
        for code in LIKERT_QUESTIONS:
            r[code] = random.randint(1, 5)

        # Variables demográficas extra (requeridas por endpoint viejo o SQL)
        r.update({
            "Demo_Pais": random.randint(1, 5),
            "Demo_Tipo_Organizacion": random.randint(1, 4),
            "Demo_Industria": random.randint(1, 18),
            "Demo_Generacion_Edad": random.randint(1, 5),
            "Demo_Genero": random.randint(1, 3),
            "Demo_Nivel_Educacion": random.randint(1, 5),
        })
        
        # Scores extra (relleno)
        s["Phish_Susceptibilidad"] = random.uniform(1.0, 5.0)
        s["Phish_Autoeficacia"] = random.uniform(1.0, 5.0)
        s["Phish_Awareness"] = random.uniform(1.0, 5.0)

        # C. INYECTAR DATOS MANUALES
        # -----------------------------------------------------
        r["Demo_Tamano_Org"] = input_tamano
        r["Demo_Rol_Trabajo"] = input_rol
        r["Demo_Horas"] = input_horas
        
        s["Big5_Apertura"] = float(input_apertura)
        s["Phish_Riesgo_Percibido"] = float(input_riesgo)
        s["Fatiga_Global_Score"] = float(input_fatiga)

        st.toast("✅ Datos generados correctamente")
        
        # D. Redirigir a Resultados
        st.session_state.page = 99
        st.rerun()