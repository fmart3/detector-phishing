import streamlit as st
import pandas as pd
import altair as alt # Usaremos gráficos nativos de Streamlit, pero importamos por si acaso
from utils.databricks import run_sql_query 

def page_dashboard():
    st.title("🛡️ Dashboard de Ciberseguridad")
    st.markdown("Monitoreo en tiempo real de la susceptibilidad al phishing organizacional.")

    # ---------------------------------------------------------
    # 1. EXTRACCIÓN DE DATOS (Una sola query eficiente)
    # ---------------------------------------------------------
    # Traemos las columnas clave para no saturar la red
    query = """
        SELECT 
            timestamp,
            probability,
            prediction,
            Demo_Rol_Trabajo,
            Fatiga_Global_Score
        FROM phishing.surveys.responses
    """
    
    df = run_sql_query(query)

    # Si no hay datos, mostramos una alerta y detenemos
    if df.empty:
        st.warning("⚠️ No se encontraron datos en la tabla 'phishing.surveys.responses'. ¿Ya hay encuestas enviadas?")
        if st.button("Reintentar conexión"):
            run_sql_query.clear()
            st.rerun()
        st.stop()

    # ---------------------------------------------------------
    # 2. SECCIÓN DE KPIs (Métricas Principales)
    # ---------------------------------------------------------
    st.subheader("📌 Estado Actual")
    
    # Cálculos en Python (rápido y flexible)
    total_encuestados = len(df)
    
    # Riesgo promedio (formato porcentaje)
    avg_risk = df['probability'].mean()
    
    # Usuarios críticos (aquellos con probabilidad > 0.5 o 50%)
    criticos = df[df['probability'] > 0.5].shape[0]

    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label="Total Encuestados", 
        value=total_encuestados
    )
    
    col2.metric(
        label="Probabilidad Promedio de Phishing", 
        value=f"{avg_risk:.1%}",
        delta_color="inverse" # Si sube es malo
    )
    
    col3.metric(
        label="🚨 Usuarios Críticos", 
        value=criticos,
        help="Usuarios con probabilidad de caer > 50%"
    )

    st.divider()

    # ---------------------------------------------------------
    # 3. RIESGO POR ROL (Gráfico)
    # ---------------------------------------------------------
    st.subheader("📊 Vulnerabilidad por Rol")

    # Mapeo de IDs a Nombres (Ajusta esto según tus valores reales del selectbox)
    rol_map = {
        1: "Administrativo", 
        2: "Técnico / TI", 
        3: "Manager / Director", 
        4: "Ejecutivo / Ventas",
        5: "Otro"
    }
    
    # Preparamos los datos para el gráfico
    # 1. Mapeamos el número al nombre
    df['Rol_Nombre'] = df['Demo_Rol_Trabajo'].map(rol_map).fillna("Desconocido")
    
    # 2. Agrupamos: Calculamos el promedio de riesgo por cada rol
    df_chart = df.groupby("Rol_Nombre")[['probability']].mean().reset_index()
    
    # 3. Ordenamos de mayor riesgo a menor
    df_chart = df_chart.sort_values(by='probability', ascending=False)

    # 4. Mostramos el gráfico
    st.bar_chart(
        df_chart, 
        x="Rol_Nombre", 
        y="probability",
        color="#FF4B4B",  # Rojo alerta
        use_container_width=True
    )
    st.caption("Eje Y: Probabilidad promedio (0.0 a 1.0)")

    # ---------------------------------------------------------
    # BOTÓN DE RECARGA MANUAL
    # ---------------------------------------------------------
    st.markdown("---")
    if st.button("🔄 Actualizar Datos en Tiempo Real"):
        run_sql_query.clear() # Borra la caché
        st.rerun() # Recarga la página

if __name__ == "__main__":
    page_dashboard()