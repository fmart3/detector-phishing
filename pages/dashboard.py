import streamlit as st
import pandas as pd
from databricks import sql
import os

# ==========================================
# 🔌 CONEXIÓN A DATABRICKS SQL
# ==========================================
def run_query(query):
    """Ejecuta una query SQL en Databricks y devuelve un DataFrame"""
    
    # Validamos que existan los secretos antes de conectar
    if "DATABRICKS_HTTP_PATH" not in st.secrets:
        st.error("❌ Falta configurar DATABRICKS_HTTP_PATH en secrets.toml")
        return pd.DataFrame()

    with sql.connect(
        server_hostname=st.secrets["DATABRICKS_HOST"].replace("https://", "").replace("http://", ""),
        http_path=st.secrets["DATABRICKS_HTTP_PATH"], # <--- AHORA SÍ LEE EL SECRETO
        access_token=st.secrets["DATABRICKS_TOKEN"]
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            # Convertir a Pandas
            if result:
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(result, columns=columns)
            return pd.DataFrame()

# ==========================================
# 📊 PÁGINA DASHBOARD
# ==========================================
def page_dashboard():
    st.title("🛡️ Dashboard de Ciberseguridad")
    st.markdown("Visión global del riesgo en la organización.")

    # 1. KPIs Generales
    kpi_query = """
    SELECT 
        COUNT(*) as total,
        AVG(probability) as riesgo_global,  -- Antes: model_output.probability
        SUM(CASE WHEN risk_level = 'ALTO' THEN 1 ELSE 0 END) as usuarios_criticos -- Antes: model_output.risk_level
    FROM phishing.surveys.responses
    """
    df_kpi = run_query(kpi_query)
    
    if not df_kpi.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Encuestados", df_kpi.iloc[0]['total'])
        col2.metric("Riesgo Promedio", f"{df_kpi.iloc[0]['riesgo_global']*100:.1f}%")
        col3.metric("🚨 Usuarios Críticos", df_kpi.iloc[0]['usuarios_criticos'])

    st.divider()

    # 2. Riesgo por Rol (Gráfico)
    st.subheader("Riesgo por Rol de Trabajo")
    risk_query = """
    SELECT 
        Demo_Rol_Trabajo as Rol,
        AVG(probability) as Riesgo  -- Antes: model_output.probability
    FROM phishing.surveys.responses
    GROUP BY 1
    ORDER BY 2 DESC
    """
    df_risk = run_query(risk_query)
    
    if not df_risk.empty:
        # Mapeo simple para que se vea bonito (si tienes los IDs)
        rol_map = {1: "Admin", 2: "Técnico", 3: "Manager", 4: "Ejecutivo"} 
        df_risk["Rol_Nombre"] = df_risk["Rol"].map(rol_map).fillna("Otro")
        
        st.bar_chart(df_risk, x="Rol_Nombre", y="Riesgo", color="#FF4B4B")

    # 3. Datos Recientes
    with st.expander("📄 Ver últimas 5 respuestas"):
        recent_query = "SELECT * FROM phishing.surveys.responses ORDER BY timestamp DESC LIMIT 5"
        st.dataframe(run_query(recent_query))

if __name__ == "__main__":
    page_dashboard()