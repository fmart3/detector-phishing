import streamlit as st
# Importamos la nueva función desde el archivo único
from utils.databricks import run_sql_query 

def page_dashboard():
    st.title("🛡️ Dashboard de Ciberseguridad")

    # 1. Consulta KPI
    df_kpi = run_sql_query("""
        SELECT COUNT(*) as total, AVG(probability) as riesgo 
        FROM phishing.surveys.responses
    """)
    
    if not df_kpi.empty:
        st.metric("Total", df_kpi.iloc[0]['total'])

    # 2. Consulta Gráfico
    df_chart = run_sql_query("SELECT * FROM ...")
    st.bar_chart(df_chart)

    # Botón para forzar actualización (borra la memoria caché)
    if st.button("Actualizar"):
        run_sql_query.clear()
        st.rerun()