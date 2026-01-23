#/utils/dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
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
    # with st.expander("🕵️ Debug: Ver columnas detectadas"):
    #     st.write(list(df.columns))
    #     st.write(df.head(2))

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
    else:
        # Aseguramos que sea numérico por si viene como texto
        df['probability'] = pd.to_numeric(df['probability'], errors='coerce').fillna(0)
        
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
        st.bar_chart(df_chart, x="Rol_Nombre", y="probability", color="#FF4B4B")
    else:
        st.warning("No se encontró la columna 'Demo_Rol_Trabajo'.")
        
    st.divider()
        
    # ---------------------------------------------------------
    # 5. ESTADO DEL MODELO
    # ---------------------------------------------------------
    st.subheader("🧠 Salud del Modelo (Estadísticas)")
    
    # A. Métricas Técnicas
    min_prob = df['probability'].min()
    max_prob = df['probability'].max()
    std_dev  = df['probability'].std()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Probabilidad Mínima", f"{min_prob:.2%}")
    m2.metric("Probabilidad Máxima", f"{max_prob:.2%}")
    
    # Lógica de color para la desviación
    # Si es muy baja (<0.01), el modelo podría estar devolviendo siempre lo mismo
    st_color = "inverse" if std_dev < 0.01 else "normal"
    m3.metric("Desviación Estándar", f"{std_dev:.3f}", delta_color=st_color)

    # B. Clasificación y Distribución
    st.markdown("##### Distribución de Niveles de Riesgo")
    
    # Función local para clasificar
    def clasificar_riesgo(prob):
        if prob < 0.30: return "🟢 Bajo"
        elif prob < 0.70: return "🟡 Medio"
        else: return "🔴 Alto"

    df['Nivel_Calculado'] = df['probability'].apply(clasificar_riesgo)

    c_chart, c_data = st.columns([2, 1])

    with c_chart:
        # Histograma simple usando Numpy para los bins
        # Crea rangos de 10% en 10% (0.0 a 1.0)
        hist_values, _ = np.histogram(df['probability'], bins=10, range=(0,1))
        # Creamos un DF para el gráfico de barras
        hist_df = pd.DataFrame({
            "Usuarios": hist_values,
            "Rango": [f"{i*10}%-{(i+1)*10}%" for i in range(10)]
        }).set_index("Rango")
        
        st.bar_chart(hist_df)
        st.caption("Histograma: ¿Cómo se agrupan las probabilidades?")

    with c_data:
        # Tabla resumen
        resumen = df['Nivel_Calculado'].value_counts().reset_index()
        resumen.columns = ['Nivel', 'Total']
        resumen['%'] = (resumen['Total'] / len(df) * 100).map('{:.1f}%'.format)
        st.dataframe(resumen, hide_index=True, use_container_width=True)

    # Botón final de recarga
    if st.button("🔄 Actualizar Dashboard"):
        run_sql_query.clear()
        st.rerun()

if __name__ == "__main__":
    page_dashboard()