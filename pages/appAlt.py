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

from utils.scoring import compute_scores

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
            options=[1, 2, 3, 4, 5, 6, 7],
            format_func=lambda x: {
                1: "100 o menos",
                2:"Entre 100 y 500",
                3:"Entre 500 y 1.000",
                4:"Entre 1.000 y 3.000",
                5:"Entre 3.000 y 10.000",
                6:"Entre 10.000 y 50.000",
                7:"Superior a 50.000"
            }[x]
        )

        input_rol = st.selectbox(
            "Rol de Trabajo",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Liderazgo (Director, Gerencia, SubGerencia, otros)", 
                2: "Supervisión y Control (Supervisor, Jefatura)", 
                3: "Administrativo, Analista, Ingeniero", 
                4: "Otro"
            }[x]
        )

        input_horas = st.selectbox(
            "Horas de Uso (Dispositivo)",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "Menos de 2 horas",
                2: "Entre 2 y 5 horas",
                3: "Entre 5 y 8 horas",
                4: "Entre 8 y 10 horas",
                5: "Más de 10 horas"
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
        st.session_state.responses = {}
        st.session_state.prediction = None
        # Nota: No ponemos st.session_state.scores = {} aquí, 
        # porque compute_scores creará el diccionario completo.
        
        r = st.session_state.responses

        # B. Generar Relleno Aleatorio (Preguntas Likert)
        # ---------------------------------------------------
        # Esto llena EX01, AM01, etc. con números del 1 al 5
        for code in LIKERT_QUESTIONS:
            r[code] = random.randint(1, 5)

        # C. Variables Demográficas
        # -----------------------------------------------------
        # Relleno aleatorio para lo que NO está en la pantalla
        r.update({
            "Demo_Pais": random.randint(1, 5),
            "Demo_Tipo_Organizacion": random.randint(1, 4),
            "Demo_Industria": random.randint(1, 18),
            "Demo_Generacion_Edad": random.randint(1, 5),
            "Demo_Genero": random.randint(1, 3),
            "Demo_Nivel_Educacion": random.randint(1, 5),
        })
        
        # Inyectar lo que el usuario eligió manualmente en los selectbox
        r["Demo_Tamano_Org"] = input_tamano
        r["Demo_Rol_Trabajo"] = input_rol
        r["Demo_Horas"] = input_horas
        
        # D. CÁLCULO DE SCORES (Paso Clave)
        # -----------------------------------------------------
        # 1. Calculamos TODOS los scores usando las respuestas aleatorias.
        # Esto evita que los scores no simulados queden en 0.
        full_scores = compute_scores(r)
        
        # 2. Guardamos ese diccionario completo en la sesión
        st.session_state.scores = full_scores

        # E. SOBRESCRIBIR CON SLIDERS MANUALES
        # -----------------------------------------------------
        # Ahora forzamos los valores de tus sliders sobre los calculados.
        st.session_state.scores["Big5_Apertura"] = float(input_apertura)
        st.session_state.scores["Phish_Riesgo_Percibido"] = float(input_riesgo)
        st.session_state.scores["Fatiga_Global_Score"] = float(input_fatiga)

        st.toast("✅ Datos generados y calculados correctamente")
        
        # F. Redirigir a Resultados
        st.session_state.page = 99
        st.rerun()
        
def page_app_alt1():
    st.markdown("## ⚡ Simulador de Escenarios (Test Rápido)")
    st.caption("Genera perfiles sintéticos para estresar el modelo y probar el Dashboard.")

    # -----------------------------------------------------
    # 0. SELECTOR DE OBJETIVO (NUEVO)
    # -----------------------------------------------------
    st.subheader("🎯 Objetivo de la Simulación")
    
    # Esto define qué tan "cargados" estarán los dados
    target_mode = st.radio(
        "¿Qué tipo de usuario quieres generar?",
        ["🎲 Aleatorio (Ruido)", "🟡 Forzar Riesgo MEDIO", "🔴 Forzar Riesgo ALTO"],
        horizontal=True
    )

    st.divider()

    # -----------------------------------------------------
    # 1. CONTROLES MANUALES (Inputs del Modelo)
    # -----------------------------------------------------
    st.subheader("🎛️ Ajustes Finos (Opcional)")
    st.info("Si seleccionas un modo arriba, estos valores se ajustarán automáticamente, pero puedes modificarlos después.")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🏢 Datos Demográficos")
        input_tamano = st.selectbox("Tamaño Org", [1,2,3,4,5,6,7], index=3)
        input_rol = st.selectbox("Rol", [1,2,3,4], format_func=lambda x: {1:"Liderazgo", 2:"Supervisión", 3:"Admin/Analista", 4:"Otro"}[x], index=2)
        input_horas = st.selectbox("Horas Uso", [1,2,3,4,5], format_func=lambda x: {1:"<2h", 2:"2-5h", 3:"5-8h", 4:"8-10h", 5:">10h"}[x], index=2)

    with col2:
        st.markdown("##### 🧠 Scores Clave")
        input_fatiga = st.slider("Fatiga Global", 1.0, 5.0, 3.0)
        input_susceptibilidad = st.slider("Susceptibilidad", 1.0, 5.0, 3.0)
        input_awareness = st.slider("Concientización (Awareness)", 1.0, 5.0, 3.0)

    # -----------------------------------------------------
    # 2. LÓGICA DE GENERACIÓN
    # -----------------------------------------------------
    if st.button("🚀 Generar Usuario Simulado", type="primary"):
        
        # A. Inicializar
        st.session_state.responses = {}
        st.session_state.prediction = None
        r = st.session_state.responses

        # B. Relleno Base (Aleatorio)
        for code in LIKERT_QUESTIONS:
            r[code] = random.randint(1, 5)

        # C. Variables Demográficas Base
        r.update({
            "Demo_Pais": random.randint(1, 5),
            "Demo_Tipo_Organizacion": random.randint(1, 4),
            "Demo_Industria": random.randint(1, 18),
            "Demo_Generacion_Edad": random.randint(1, 5),
            "Demo_Genero": random.randint(1, 3),
            "Demo_Nivel_Educacion": random.randint(1, 5),
            "Demo_Tamano_Org": input_tamano,
            "Demo_Rol_Trabajo": input_rol,
            "Demo_Horas": input_horas
        })

        # D. Calcular Scores Iniciales
        full_scores = compute_scores(r)
        st.session_state.scores = full_scores

        # =========================================================
        # 🔥 E. INYECCIÓN DE SESGO (AQUÍ OCURRE LA MAGIA)
        # =========================================================
        
        # SI QUEREMOS RIESGO ALTO 🔴
        if target_mode == "🔴 Forzar Riesgo ALTO":
            # 1. Demografía Peligrosa (Basado en tu análisis anterior)
            r["Demo_Horas"] = 5         # > 10 horas (Fatiga)
            r["Demo_Rol_Trabajo"] = 3   # Administrativo (Expuesto)
            r["Demo_Industria"] = random.choice([11, 12, 16]) # Minería, Oil&Gas, Construcción
            
            # 2. Psicología Vulnerable (Sobrescribimos los scores calculados)
            # Usamos "uniform" para que varíe un poco y no sea siempre el mismo número
            st.session_state.scores["Fatiga_Global_Score"] = random.uniform(4.2, 5.0)   # Muy cansado
            st.session_state.scores["Phish_Susceptibilidad"] = random.uniform(4.0, 5.0) # Muy créulo
            st.session_state.scores["Phish_Awareness"] = random.uniform(1.0, 2.0)       # No sabe nada
            st.session_state.scores["Big5_Responsabilidad"] = random.uniform(1.0, 2.5)  # Desordenado
            st.session_state.scores["Big5_Neuroticismo"] = random.uniform(3.5, 5.0)     # Ansioso

        # SI QUEREMOS RIESGO MEDIO 🟡
        elif target_mode == "🟡 Forzar Riesgo MEDIO":
            r["Demo_Horas"] = random.choice([3, 4]) # 5-10 horas
            r["Demo_Rol_Trabajo"] = random.choice([2, 3]) 
            
            st.session_state.scores["Fatiga_Global_Score"] = random.uniform(2.8, 3.8)
            st.session_state.scores["Phish_Susceptibilidad"] = random.uniform(2.5, 3.5)
            st.session_state.scores["Phish_Awareness"] = random.uniform(2.5, 3.5)

        # SI ES MANUAL / ALEATORIO (Respetamos los Sliders) 🎲
        else:
            # Sobrescribimos solo con lo que moviste en los sliders visuales
            st.session_state.scores["Fatiga_Global_Score"] = float(input_fatiga)
            st.session_state.scores["Phish_Susceptibilidad"] = float(input_susceptibilidad)
            st.session_state.scores["Phish_Awareness"] = float(input_awareness)
            # Los demográficos ya se tomaron de los inputs arriba

        st.toast(f"✅ Usuario generado: {target_mode}")
        
        # F. Redirigir
        st.session_state.page = 99
        st.rerun()