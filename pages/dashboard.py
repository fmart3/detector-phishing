#/utils/dashboard.py

import streamlit as st
import pandas as pd
from utils.databricks import run_sql_query 

def page_dashboard():
    st.title("🛡️ Dashboard de Ciberseguridad")
    
    # ---------------------------------------------------------
    # 1. DIAGNÓSTICO DE COLUMNAS (Para ver qué tienes realmente)
    # ---------------------------------------------------------
    # Usamos SELECT * para que no falle si falta una columna específica
    query = "SELECT * FROM phishing.surveys.responses"
    df = run_sql_query(query)

    if df.empty:
        st.warning("⚠️ La tabla existe pero está vacía (0 filas).")
        if st.button("Recargar"):
            run_sql_query.clear()
            st.rerun()
        st.stop()

    # Muestra las columnas que REALMENTE existen (Solo visible para ti, el admin)
    with st.expander("🕵️ Debug: Ver columnas detectadas"):
        st.write(list(df.columns))
        st.write(df.head(2))

    # ---------------------------------------------------------
    # 2. VALIDACIÓN DE DATOS
    # ---------------------------------------------------------
    # Verificamos si tenemos las columnas del modelo. 
    # Si no existen, creamos datos falsos (ceros) para que el dashboard no explote.
    
    if 'probability' not in df.columns:
        st.error("⚠️ ALERTA: La columna 'probability' no existe en la base de datos.")
        st.info("💡 Solución: Debemos revisar la función de guardado en App.py.")
        # Rellenamos con 0 para poder visualizar el resto del dashboard
        df['probability'] = 0.0
        
    if 'prediction' not in df.columns:
        df['prediction'] = 0

    # ---------------------------------------------------------
    # 3. KPIs (Ahora seguros)
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Encuestados", len(df))
    col2.metric("Riesgo Promedio", f"{df['probability'].mean():.1%}")
    col3.metric("Usuarios Críticos", df[df['probability'] > 0.5].shape[0])

    st.divider()

    # ---------------------------------------------------------
    # 4. GRÁFICO DE RIESGO POR ROL
    # ---------------------------------------------------------
    st.subheader("📊 Riesgo por Rol")
    
    if 'Demo_Rol_Trabajo' in df.columns:
        rol_map = {1: "Liderazgo", 2: "Supervisión", 3: "Administrativo", 4: "Otro"}
        # Convertimos a numérico por seguridad y mapeamos
        df['Rol_Nombre'] = pd.to_numeric(df['Demo_Rol_Trabajo'], errors='coerce').map(rol_map).fillna("Otro")
        
        df_chart = df.groupby("Rol_Nombre")[['probability']].mean().reset_index()
        st.bar_chart(df_chart, x="Rol de Trabajo", y="Probabilidad de Riesgo", color="#FF4B4B")
    else:
        st.warning("No se encontró la columna 'Demo_Rol_Trabajo'.")

if __name__ == "__main__":
    page_dashboard()