import streamlit as st
import requests
import json

# --- 1. CONFIGURACIÓN Y SECRETOS ---
st.set_page_config(page_title="Diagnóstico Ciberseguridad", page_icon="🛡️")

try:
    DATABRICKS_URL = st.secrets["DATABRICKS_URL"]
    DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]
except FileNotFoundError:
    st.error("Error: Configura los 'Secrets' en Streamlit Cloud.")
    st.stop()

# --- 2. FUNCIÓN PARA LEER URL ---
def get_param(key, default=0.0):
    # Busca el parámetro en la URL, si falla devuelve 0
    params = st.query_params
    if key in params:
        try:
            return float(params[key])
        except:
            return default
    return default

# --- 3. CAPTURA DE DATOS (Mapeo Qualtrics -> Modelo) ---
# Leemos los 16 inputs exactos que pide tu modelo
# NOTA: Asumimos que Qualtrics envía el PROMEDIO. Si envía SUMA, divide aquí (ej: /10)

# Big 5
b5_extra = get_param("b5_ext")
b5_amab = get_param("b5_ama")
b5_resp = get_param("b5_res")
b5_neur = get_param("b5_neu")
b5_aper = get_param("b5_ape")

# Factores Phishing
ph_actitud = get_param("ph_act")
ph_aware = get_param("ph_awa")
ph_riesgo = get_param("ph_rie")
ph_autoeficacia = get_param("ph_aut")
ph_susc = get_param("ph_sus")

# Fatiga
fatiga = get_param("fatiga")

# Demográficos
demo_edad = get_param("edad")
demo_pais = get_param("pais") 
demo_edu = get_param("edu")
demo_horas = get_param("horas")
demo_rol = get_param("rol")

# Detectamos si hay datos reales (si la suma es > 0, es que vino de la encuesta)
hay_datos = (fatiga > 0) or (demo_edad > 0)

# --- 4. INTERFAZ VISUAL ---
st.title("🛡️ Diagnóstico de Susceptibilidad")

if not hay_datos:
    st.info("👋 Hola. Para ver tu resultado, por favor completa primero la encuesta.")
    st.markdown("[Ir a la Encuesta](https://tucorreo.qualtrics.com/...)") # Pon aquí tu link de Qualtrics
else:
    # --- 5. INVOCACIÓN AL MODELO ---
    with st.spinner("Analizando tu perfil psicológico..."):
        
        # Lista exacta de 16 columnas en el ORDEN de entrenamiento
        columnas = [
            'Big5_Extraversion', 'Big5_Amabilidad', 'Big5_Responsabilidad', 
            'Big5_Neuroticismo', 'Big5_Apertura', 'Phish_Actitud_Riesgo', 
            'Phish_Awareness', 'Phish_Riesgo_Percibido', 'Phish_Autoeficacia', 
            'Phish_Susceptibilidad', 'Fatiga_Global_Score', 'Demo_Generacion_Edad', 
            'Demo_Pais', 'Demo_Nivel_Educacion', 'Demo_Horas', 'Demo_Rol_Trabajo'
        ]
        
        datos = [
            b5_extra, b5_amab, b5_resp, b5_neur, b5_aper,
            ph_actitud, ph_aware, ph_riesgo, ph_autoeficacia, ph_susc,
            fatiga, demo_edad, demo_pais, demo_edu, demo_horas, demo_rol
        ]
        
        # Payload para Databricks
        payload = {"dataframe_split": {"columns": columnas, "data": [datos]}}
        headers = {"Authorization": f"Bearer {DATABRICKS_TOKEN}", "Content-Type": "application/json"}

        try:
            response = requests.post(DATABRICKS_URL, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                prediccion = response.json()['predictions'][0]
                
                st.divider()
                if prediccion == 1:
                    st.error("⚠️ RESULTADO: ALTA VULNERABILIDAD")
                    st.write("Tu perfil indica que podrías ser susceptible a engaños digitales sofisticados.")
                    st.markdown("""
                    **Recomendaciones:**
                    * Desconfía de correos urgentes.
                    * Verifica siempre el remitente.
                    """)
                else:
                    st.success("✅ RESULTADO: PERFIL SEGURO")
                    st.write("Tienes buenos mecanismos de defensa contra el Phishing. ¡Mantente alerta!")
                    
                # (Opcional) Debug para ver qué datos llegaron
                with st.expander("Ver mis datos procesados"):
                    st.write(payload)
            else:
                st.error(f"Error técnico en el modelo: {response.text}")
                
        except Exception as e:
            st.error(f"Error de conexión: {e}")
