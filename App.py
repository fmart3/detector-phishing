import streamlit as st
import requests
import json

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Diagnóstico Ciberseguridad", page_icon="🛡️", layout="centered")

# CSS simple para ocultar elementos innecesarios
st.markdown("""
<style>
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Recuperar secretos
try:
    DATABRICKS_URL = st.secrets["DATABRICKS_URL"]
    DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]
except FileNotFoundError:
    st.error("Error: Configura los 'Secrets' en Streamlit Cloud.")
    st.stop()

st.title("🛡️ Evaluación de Susceptibilidad")
st.write("Responde las siguientes preguntas para obtener tu perfil de riesgo.")

# --- 2. EL FORMULARIO (Sustituye a Qualtrics) ---
with st.form("encuesta_form"):
    
    # --- A. DEMOGRÁFICOS ---
    st.subheader("1. Datos Generales")
    col1, col2 = st.columns(2)
    
    with col1:
        # Mapeo: El usuario ve texto, pero el modelo recibe números
        # Ajusta estos números según cómo entrenaste tu modelo (Label Encoding)
        edad_opt = st.selectbox("Generación", options=["Gen Z", "Millennial", "Gen X", "Boomer"])
        map_edad = {"Gen Z": 1, "Millennial": 2, "Gen X": 3, "Boomer": 4}
        
        pais_opt = st.selectbox("País", ["Chile", "México", "España", "Otro"])
        map_pais = {"Chile": 1, "México": 2, "España": 3, "Otro": 0}

        edu_opt = st.selectbox("Nivel Educacional", ["Media", "Técnico", "Universitario", "Postgrado"])
        map_edu = {"Media": 1, "Técnico": 2, "Universitario": 3, "Postgrado": 4}

    with col2:
        horas = st.slider("Horas diarias en internet", 1, 24, 8)
        
        rol_opt = st.selectbox("Rol", ["Operativo", "Administrativo", "Gerencial", "TI"])
        map_rol = {"Operativo": 1, "Administrativo": 2, "Gerencial": 3, "TI": 4}

    st.markdown("---")

    # --- B. PREGUNTAS (Simuladas para el cálculo) ---
    # Para no escribir 50 sliders, aquí agrupamos por categorías.
    # El usuario responde del 1 al 5.
    
    st.subheader("2. Personalidad (Big 5)")
    st.info("Responde qué tanto te identificas (1: Nada, 5: Totalmente)")
    
    # Ejemplo Big5 - Extraversión
    b5_e1 = st.slider("Me siento cómodo con la gente", 1, 5, 3)
    b5_e2 = st.slider("Inicio conversaciones fácilmente", 1, 5, 3)
    # Cálculo interno del score (promedio)
    score_extraversion = (b5_e1 + b5_e2) / 2 

    # Agregamos placeholders para el resto (TÚ DEBES AGREGAR TUS PREGUNTAS REALES AQUÍ)
    # Por ahora usaré sliders directos para simular el promedio de la categoría
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        score_amabilidad = st.slider("Nivel de Amabilidad (Promedio)", 1.0, 5.0, 3.0, step=0.1)
        score_responsabilidad = st.slider("Nivel de Responsabilidad (Promedio)", 1.0, 5.0, 3.0, step=0.1)
    with col_b2:
        score_neuroticismo = st.slider("Nivel de Neuroticismo (Promedio)", 1.0, 5.0, 3.0, step=0.1)
        score_apertura = st.slider("Nivel de Apertura (Promedio)", 1.0, 5.0, 3.0, step=0.1)

    st.markdown("---")

    st.subheader("3. Factores de Ciberseguridad")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        score_ph_actitud = st.slider("Actitud al Riesgo", 1.0, 5.0, 3.0)
        score_ph_aware = st.slider("Conciencia (Awareness)", 1.0, 5.0, 3.0)
        score_ph_riesgo = st.slider("Riesgo Percibido", 1.0, 5.0, 3.0)
    with col_p2:
        score_ph_autoeficacia = st.slider("Autoeficacia", 1.0, 5.0, 3.0)
        score_ph_susceptibilidad = st.slider("Susceptibilidad General", 1.0, 5.0, 3.0)
    
    st.markdown("---")
    score_fatiga = st.slider("Nivel de Fatiga Global", 1.0, 7.0, 3.5) # Asumiendo escala 1-7

    # BOTÓN DE ENVÍO
    submitted = st.form_submit_button("Analizar mi Perfil 🚀", type="primary")

# --- 3. LÓGICA DE ENVÍO Y PREDICCIÓN ---
if submitted:
    
    # Preparar los datos numéricos (Mapear textos a números)
    val_edad = map_edad[edad_opt]
    val_pais = map_pais[pais_opt]
    val_edu = map_edu[edu_opt]
    val_rol = map_rol[rol_opt]

    # Crear la lista de datos en el ORDEN EXACTO del modelo
    columnas = [
        'Big5_Extraversion', 'Big5_Amabilidad', 'Big5_Responsabilidad', 
        'Big5_Neuroticismo', 'Big5_Apertura', 'Phish_Actitud_Riesgo', 
        'Phish_Awareness', 'Phish_Riesgo_Percibido', 'Phish_Autoeficacia', 
        'Phish_Susceptibilidad', 'Fatiga_Global_Score', 'Demo_Generacion_Edad', 
        'Demo_Pais', 'Demo_Nivel_Educacion', 'Demo_Horas', 'Demo_Rol_Trabajo'
    ]
    
    datos = [
        score_extraversion, score_amabilidad, score_responsabilidad, 
        score_neuroticismo, score_apertura, score_ph_actitud, 
        score_ph_aware, score_ph_riesgo, score_ph_autoeficacia, 
        score_ph_susceptibilidad, score_fatiga, val_edad, 
        val_pais, val_edu, horas, val_rol
    ]

    # --- 4. LLAMADA A DATABRICKS ---
    with st.spinner("Conectando con el cerebro de IA..."):
        payload = {"dataframe_split": {"columns": columnas, "data": [datos]}}
        headers = {"Authorization": f"Bearer {DATABRICKS_TOKEN}", "Content-Type": "application/json"}

        try:
            # Enviamos a tu modelo existente
            response = requests.post(DATABRICKS_URL, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                prediccion = response.json()['predictions'][0]
                
                st.divider()
                if prediccion == 1: # Asumiendo 1 = Riesgo
                    st.error("⚠️ RESULTADO: ALTA VULNERABILIDAD")
                    st.write("Tu perfil indica riesgo de caer en Phishing.")
                else:
                    st.success("✅ RESULTADO: PERFIL SEGURO")
                    st.write("Tienes buena resistencia, ¡sigue así!")
                
                # Debug (Opcional, borrar en producción)
                with st.expander("Ver datos técnicos"):
                    st.json(payload)
            else:
                st.error(f"Error del modelo: {response.text}")

        except Exception as e:
            st.error(f"Error de conexión: {e}")
