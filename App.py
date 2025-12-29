import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURACIÓN (Rellena esto con tus datos) ---
try:
    DATABRICKS_URL = st.secrets["DATABRICKS_URL"]
    DATABRICKS_TOKEN = st.secrets["DATABRICKS_TOKEN"]
except FileNotFoundError:
    st.error("Error: No se encontraron los secretos. Configúralos en Streamlit Cloud.")
    st.stop()

# --- INTERFAZ WEB ---
st.title("🕵️ Detector de Phishing en Tiempo Real")
st.write("Basado en tus respuestas de la encuesta, analizamos tu nivel de riesgo.")

# Simulación de recibir datos de Qualtrics (o formulario manual)
# IMPORTANTE: El orden de estas preguntas debe ser IDÉNTICO a X_train
with st.form("encuesta_phishing"):
    edad = st.number_input("Edad", min_value=10, max_value=100, value=25)
    tiempo_internet = st.number_input("Tiempo en internet (min/día)", value=120)
    correos_diarios = st.number_input("Correos recibidos al día", value=20)
    # ... Agrega aquí el resto de tus campos de la encuesta ...
    
    boton_enviar = st.form_submit_button("Analizar Riesgo")

if boton_enviar:
    # 1. Preparar los datos
    # Creamos una lista con los valores en el MISMO ORDEN que entrenaste
    datos_usuario = [edad, tiempo_internet, correos_diarios] 
    # NOTA: Asegúrate de completar esta lista con TODAS las columnas que usó el modelo
    
    columns = ["edad", "tiempo_internet", "correos_diarios"] # Nombres de tus columnas
    
    # 2. Empaquetar para Databricks
    payload = {
        "dataframe_split": {
            "columns": columns,
            "data": [datos_usuario]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    # 3. Enviar al modelo
    with st.spinner('Consultando a la Inteligencia Artificial...'):
        try:
            response = requests.post(DATABRICKS_URL, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                # La respuesta suele venir en 'predictions'
                prediccion = result['predictions'][0]
                
                if prediccion == 1:
                    st.error("⚠️ ALERTA: Tu perfil indica ALTA SUCEPTIBILIDAD al Phishing.")
                    st.write("Consejo: Revisa siempre el remitente de los correos.")
                else:
                    st.success("✅ SEGURO: Tu perfil indica un comportamiento ciberseguro.")
            else:
                st.error(f"Error en la conexión: {response.text}")
                
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")