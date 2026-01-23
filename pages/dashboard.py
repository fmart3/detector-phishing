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
    query = "SELECT * FROM phishing.surveys.responses WHERE timestamp < '2026-01-21T11:56:07';"
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
    # Verificamos si tenemos las columnas del modelo
    
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
    # 3. KPIs
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Encuestados", len(df))
    col2.metric("Riesgo Promedio", f"{df['probability'].mean():.1%}")
    col3.metric("Usuarios Críticos", df[df['probability'] > 0.5].shape[0])

    st.divider()

    # ---------------------------------------------------------
    # 4. SALUD DEL MODELO
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
        
    # ---------------------------------------------------------
    # 5. CAPA DE RIESGO
    # ---------------------------------------------------------
    st.header("🎯 Riesgo Operacional")
    st.markdown("Identificación de segmentos vulnerables para priorizar capacitación.")

    # --- MAPEOS (Ajusta estos diccionarios a tu encuesta real) ---
    map_rol = {
        1: "Liderazgo (Director, Gerencia, SubGerencia, otros)",
        2: "Supervisión y Control (Supervisor, Jefatura)",
        3: "Administrativo, Analista, Ingeniero",
        4: "Otra"
    }
    map_ind = {
        1: "Agricultura",
        2: "Bancos/Financiera",
        3: "Seguros",
        4: "TI",
        5: "Publi., Market., Coms.",
        6: "Transporte",
        7: "Salud Privada",
        8: "AFP",
        9: "Sector Público",
        10: "Energia",
        11: "Mineria",
        12: "Oil & Gas",
        13: "Retail",
        14: "Educación",
        15: "Serv. Prof. y/o Consul.",
        16: "Construcción",
        17: "Manufactura",
        18: "Otras"
    }
    map_tam = {
        1: "< 100 Emp",
        2: "100-500 Emp",
        3: "500-1.000 Emp",
        4: "1.000-3.000 Emp",
        5: "3.000-10.000 Emp",
        6: "10.000-50.000 Emp",
        7: "> 50.000 Emp"
    }
    map_hor = {
        1: "< 2 horas",
        2: "2-5 horas",
        3: "5-8 horas",
        4: "8-10 horas",
        5: "> 10 horas"
    }
    # Aplicamos mapeos si las columnas existen
    if 'Demo_Rol_Trabajo' in df.columns:
        df['Rol_Label'] = df['Demo_Rol_Trabajo'].map(map_rol).fillna("Sin respuesta")
    if 'Demo_Industria' in df.columns:
        df['Ind_Label'] = df['Demo_Industria'].map(map_ind).fillna("Sin respuesta")
    if 'Demo_Tamano_Org' in df.columns:
        df['Org_Label'] = df['Demo_Tamano_Org'].map(map_tam).fillna("Sin respuesta")
    if 'Demo_Horas' in df.columns:
        df['Horas_Label'] = df['Demo_Horas'].map(map_hor).fillna("Sin respuesta")

    # --- PESTAÑAS DE ANÁLISIS ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏭 Industria", "⏰ Horas PC", "🏢 Tamaño Org", "👤 Rol"])

    def plot_risk_by(col_label, tab_obj, color="#FF4B4B"):
        """Función auxiliar para graficar rápido"""
        if col_label in df.columns:
            # Agrupar, sacar promedio, ordenar
            data = df[df[col_label] != "Sin respuesta"]
            data = df.groupby(col_label)[['probability']].mean().sort_values('probability', ascending=False)
            with tab_obj:
                st.bar_chart(data, color=color)
                # Insight automático
                top_seg = data.index[0]
                top_val = data.iloc[0,0]
                st.caption(f"📍 El segmento más riesgoso es **{top_seg}** con {top_val:.1%} de probabilidad.")
        else:
            tab_obj.warning(f"Falta columna para {col_label}")

    # Generamos los gráficos en cada tab
    plot_risk_by('Ind_Label', tab1, "#1f77b4")   # Azul
    plot_risk_by('Horas_Label', tab2, "#ff7f0e") # Naranja
    plot_risk_by('Org_Label', tab3, "#2ca02c")   # Verde
    plot_risk_by('Rol_Label', tab4, "#d62728")   # Rojo

    st.divider()
    
    # ==========================================
    # 🚨 6. TOP USUARIOS CRÍTICOS (Anonimizado)
    # ==========================================
    st.subheader("🚨 Top 10 Usuarios de Mayor Riesgo")
    st.markdown("Listado anonimizado para auditoría prioritaria.")

    # Columnas a mostrar (Solo las que aportan valor sin revelar identidad directa)
    cols_to_show = ['probability']
    
    # Agregamos las etiquetas si existen
    if 'Org_Label' in df.columns: cols_to_show.insert(2, 'Org_Label')
    if 'Rol_Label' in df.columns: cols_to_show.insert(0, 'Rol_Label')
    if 'Ind_Label' in df.columns: cols_to_show.insert(1, 'Ind_Label')
    if 'Horas_Label' in df.columns: cols_to_show.append('Horas_Label')

    # Filtramos y ordenamos
    top_risk = df.sort_values(by='probability', ascending=False).head(10)
    
    # Mostramos tabla con formato bonito
    st.dataframe(
        top_risk[cols_to_show],
        use_container_width=True,
        hide_index=True,
        column_config={
            "probability": st.column_config.ProgressColumn(
                "Nivel de Riesgo",
                help="Probabilidad de caer en phishing",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "Org_Label": "Tamaño Org",
            "Rol_Label": "Rol",
            "Ind_Label": "Industria",
            "Horas_Label": "Tiempo en Pantalla"
        }
    )
    
    # ==========================================
    # 🧬 7. CAPA INTERPRETABILIDAD (Alto vs Bajo)
    # ==========================================
    st.header("🧬 Análisis de Comportamiento (Interpretabilidad)")
    st.markdown("¿Qué diferencia psicológicamente a los usuarios vulnerables de los seguros?")

    # 1. DEFINIR LAS COLUMNAS A ANALIZAR
    # ------------------------------------------------------
    # ⚠️ IMPORTANTE: Ajusta esta lista con los nombres EXACTOS de tus columnas en Databricks.
    # He puesto los nombres comunes, pero verifica si se llaman "Big5_Openness" o "Apertura", etc.
    features_psicologicas = [
        "Big5_Extraversion",
        "Big5_Amabilidad",
        "Big5_Responsabilidad",
        "Big5_Neuroticismo",
        "Big5_Apertura",
        "Phish_Actitud_Riesgo",
        "Phish_Awareness",
        "Phish_Riesgo_Percibido",
        "Phish_Autoeficacia",
        "Phish_Susceptibilidad",
        "Fatiga_Global_Score"
    ]
    
    # Filtramos solo las que realmente existan en el DF para no dar error
    features_reales = [c for c in features_psicologicas if c in df.columns]

    if len(features_reales) == 0:
        st.warning("⚠️ No se encontraron columnas de Psicología/Fatiga (ej. Big5, Fatiga). Revisa la lista 'features_psicologicas' en el código.")
    
    else:
        # 2. CREAR GRUPOS (Alto vs Bajo)
        # ------------------------------------------------------
        # Definimos el corte en 50% (0.5)
        df['Grupo_Analisis'] = df['probability'].apply(lambda x: '🔴 Alto Riesgo (>50%)' if x > 0.5 else '🟢 Bajo Riesgo (<50%)')
        
        # Validamos que existan ambos grupos para poder comparar
        if len(df['Grupo_Analisis'].unique()) < 2:
            st.info("ℹ️ Todos los usuarios están en el mismo grupo de riesgo. Necesitamos variedad para comparar.")
        else:
            # 3. CÁLCULO DE PROMEDIOS
            # ------------------------------------------------------
            # Agrupamos y sacamos la media de las columnas psicológicas
            comparativa = df.groupby('Grupo_Analisis')[features_reales].mean().reset_index()
            
            # Transponemos la tabla para que sea más fácil de graficar (Filas = Features)
            comp_t = comparativa.set_index('Grupo_Analisis').transpose()
            comp_t.columns = ['Bajo Riesgo', 'Alto Riesgo'] if comp_t.columns[0].startswith('🟢') else ['Alto Riesgo', 'Bajo Riesgo']
            
            # Calculamos la diferencia porcentual para ordenar el gráfico
            # (Cuánto más alto es el valor en el grupo de riesgo comparado con el seguro)
            # Evitamos división por cero sumando un pequeño epsilon
            comp_t['Diferencia'] = comp_t['Alto Riesgo'] - comp_t['Bajo Riesgo']
            
            # Ordenamos por la diferencia más grande (Lo que más impacta)
            comp_t = comp_t.sort_values(by='Diferencia', ascending=False)

            # 4. VISUALIZACIÓN
            # ------------------------------------------------------
            c_izq, c_der = st.columns([2, 1])

            with c_izq:
                st.subheader("Comparativa de Perfiles")
                st.caption("Valores promedio de cada factor según el grupo de riesgo.")
                
                # Graficamos Alto vs Bajo lado a lado
                st.bar_chart(comp_t[['Alto Riesgo', 'Bajo Riesgo']], use_container_width=True)
            
            with c_der:
                st.subheader("💡 Insights")
                
                # Encontramos el factor más diferenciador
                top_factor = comp_t.index[0]
                diff_val = comp_t.iloc[0]['Diferencia']
                
                st.markdown(f"""
                El factor que más distingue a los usuarios de alto riesgo es **{top_factor}**.
                
                En promedio, el grupo vulnerable tiene un puntaje **{diff_val:+.2f} puntos** mayor en esta escala que el grupo seguro.
                """)
                
                st.dataframe(
                    comp_t.style.background_gradient(cmap="Reds", subset=['Alto Riesgo'])
                                .background_gradient(cmap="Greens", subset=['Bajo Riesgo'])
                                .format("{:.2f}"),
                    use_container_width=True
                )

    # Botón final de recarga
    if st.button("🔄 Actualizar Dashboard"):
        run_sql_query.clear()
        st.rerun()

if __name__ == "__main__":
    page_dashboard()