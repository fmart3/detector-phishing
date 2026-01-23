#/utils/dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
from utils.databricks import run_sql_query 

def page_dashboard():
    # Configuración de la página (Opcional, pero recomendado para iniciar colapsado)
    st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="collapsed")
    
    # ---------------------------------------------------------
    # 🪄 TRUCO CSS: OCULTAR LA NAVEGACIÓN LATERAL
    # ---------------------------------------------------------
    no_sidebar_style = """
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """
    st.markdown(no_sidebar_style, unsafe_allow_html=True)

    st.title("🛡️ Dashboard de Ciberseguridad")
    
    # ---------------------------------------------------------
    # 1. DIAGNÓSTICO DE COLUMNAS (Para ver qué tienes realmente)
    # ---------------------------------------------------------
    # Usamos SELECT * para que no falle si falta una columna específica
    query = "SELECT * FROM phishing.surveys.responses WHERE timestamp > '2026-01-21T11:56:07';"
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
    # 4. SALUD DEL MODELO (Lógica consistente con BD)
    # ---------------------------------------------------------
    st.subheader("🧠 Salud del Modelo (Estadísticas)")
    
    # A. Métricas Técnicas (Se mantiene igual)
    min_prob = df['probability'].min()
    max_prob = df['probability'].max()
    std_dev  = df['probability'].std()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Probabilidad Mínima", f"{min_prob:.2%}")
    m2.metric("Probabilidad Máxima", f"{max_prob:.2%}")
    
    st_color = "inverse" if std_dev < 0.01 else "normal"
    m3.metric("Desviación Estándar", f"{std_dev:.3f}", delta_color=st_color)

    # B. Clasificación y Distribución (CORREGIDO: Usando risk_level de la BD)
    st.markdown("##### Distribución de Niveles de Riesgo")

    # Verificamos si existe la columna en la BD
    col_riesgo_db = 'risk_level' # Asegúrate que este sea el nombre exacto en tu tabla
    
    if col_riesgo_db in df.columns:
        # Llenamos nulos por seguridad
        df[col_riesgo_db] = df[col_riesgo_db].fillna("Sin Clasificar")

        # (Opcional) Diccionario para agregar emojis a lo que viene de la BD
        # Ajusta las claves (Low/Bajo) según lo que realmente guardes en App.py
        emoji_map = {
            "Low": "🟢 Low",   "Bajo": "🟢 Bajo",
            "Medium": "🟡 Medium", "Medio": "🟡 Medio",
            "High": "🔴 High",  "Alto": "🔴 Alto"
        }
        
        # Creamos columna visual mapeando el valor de la BD
        # Si el valor no está en el mapa, muestra el texto original tal cual
        df['Nivel_Display'] = df[col_riesgo_db].map(lambda x: emoji_map.get(x, x))
    else:
        st.error(f"⚠️ No se encontró la columna '{col_riesgo_db}' en la base de datos.")
        df['Nivel_Display'] = "Error de Datos"

    c_chart, c_data = st.columns([2, 1])

    with c_chart:
        # El histograma usa 'probability' (matemática pura), eso está bien
        hist_values, _ = np.histogram(df['probability'], bins=10, range=(0,1))
        hist_df = pd.DataFrame({
            "Usuarios": hist_values,
            "Rango": [f"{i*10}%-{(i+1)*10}%" for i in range(10)]
        }).set_index("Rango")
        
        st.bar_chart(hist_df)
        st.caption("Histograma: Distribución matemática de probabilidades")

    with c_data:
        # Tabla resumen: AHORA CUENTA LO QUE HAY EN LA BD (Consistencia Total)
        resumen = df['Nivel_Display'].value_counts().reset_index()
        resumen.columns = ['Nivel (BD)', 'Total']
        resumen['%'] = (resumen['Total'] / len(df) * 100).map('{:.1f}%'.format)
        
        st.dataframe(resumen, hide_index=True, use_container_width=True)
        
    # ---------------------------------------------------------
    # 5. CAPA DE RIESGO
    # ---------------------------------------------------------
    st.header("🎯 Riesgo Operacional")
    st.markdown("Identificación de segmentos vulnerables para priorizar capacitación.")

    # --- MAPEOS (Ajusta estos diccionarios a tu encuesta real) ---
    map_rol = {
        1: "Liderazgo",
        2: "Supervisión",
        3: "Administrativo",
        4: "Otro"
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
        18: "Otra"
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
    if 'Org_Label' in df.columns: cols_to_show.insert(1, 'Org_Label')
    if 'Rol_Label' in df.columns: cols_to_show.insert(2, 'Rol_Label')
    if 'Ind_Label' in df.columns: cols_to_show.insert(3, 'Ind_Label')
    if 'Horas_Label' in df.columns: cols_to_show.insert(4,'Horas_Label')

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
    
    st.divider()
    
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
    
    features_reales = [c for c in features_psicologicas if c in df.columns]

    if len(features_reales) == 0:
        st.warning("⚠️ No se encontraron columnas de comportamiento. Revisa la lista 'features_psicologicas'.")
    
    else:
        # 2. CREAR GRUPOS
        df['Grupo_Analisis'] = df['probability'].apply(lambda x: '🔴 Alto Riesgo' if x > 0.5 else '🟢 Bajo Riesgo')
        
        if len(df['Grupo_Analisis'].unique()) < 2:
            st.info("ℹ️ Necesitamos usuarios de alto y bajo riesgo para comparar.")
        else:
            # 3. CÁLCULO
            comparativa = df.groupby('Grupo_Analisis')[features_reales].mean().reset_index()
            
            # Transponer para gráfico
            comp_t = comparativa.set_index('Grupo_Analisis').transpose()
            # Ajuste de columnas dinámico
            cols_ordenadas = sorted(comp_t.columns.tolist()) # Para asegurar orden consistente
            comp_t = comp_t[cols_ordenadas]
            
            # Calcular Diferencia (Si hay 2 columnas)
            if len(comp_t.columns) == 2:
                # Asumimos que la columna de "Alto Riesgo" es la que tiene el icono rojo o empieza con A
                col_alto = [c for c in comp_t.columns if "Alto" in c][0]
                col_bajo = [c for c in comp_t.columns if "Bajo" in c][0]
                comp_t['Diferencia'] = abs(comp_t[col_alto] - comp_t[col_bajo])
                comp_t = comp_t.sort_values(by='Diferencia', ascending=False)
                
                # Insight Automático
                top_factor = comp_t.index[0]
                diff_val = comp_t.iloc[0]['Diferencia']
                insight_text = f"El factor más determinante es **{top_factor}** ({diff_val:+.2f} puntos de diferencia)."
            else:
                insight_text = "Se muestran los valores promedio por grupo."

            # 4. VISUALIZACIÓN (NUEVO LAYOUT VERTICAL)
            # ------------------------------------------------------
            
            # A. Insight Texto
            st.info(f"💡 **Hallazgo Clave:** {insight_text}")

            # B. Gráfico (Ancho completo)
            st.subheader("📊 Comparativa Visual")
            st.bar_chart(comp_t[[c for c in comp_t.columns if c != 'Diferencia']], use_container_width=True)

            # C. Tabla de Datos (Abajo y Ancha)
            st.subheader("📋 Detalle de Datos")
            st.dataframe(
                comp_t.style.background_gradient(cmap="Reds", subset=[col_alto] if 'col_alto' in locals() else None)
                            .background_gradient(cmap="Greens", subset=[col_bajo] if 'col_bajo' in locals() else None)
                            .format("{:.2f}"),
                use_container_width=True  # <--- ESTO HACE QUE OCUPE TODO EL ANCHO
            )
            
    st.divider()
    # ==========================================
    # ⚠️ 8. MONITOR DE SALUD DEL MODELO (AUDITORÍA ESTADÍSTICA)
    # ==========================================
    st.header("⚙️ Auditoría Técnica del Modelo")
    st.markdown("Diagnóstico estadístico para validar la confiabilidad de las predicciones.")

    # 1. PREPARACIÓN DE DATOS ESTADÍSTICOS
    # ------------------------------------------------------
    stats = df['probability'].describe()
    
    # Calculamos métricas adicionales
    skewness = df['probability'].skew() # Sesgo: ¿Hacia dónde se inclina la curva?
    kurtosis = df['probability'].kurt() # Curtosis: ¿Qué tan "picuda" es la curva?
    iqr = stats['75%'] - stats['25%']   # Rango Intercuartil (donde está el 50% central de la gente)

    # 2. TABLA DE JUSTIFICACIÓN (Valores vs Esperados)
    # ------------------------------------------------------
    st.subheader("📋 Indicadores de Calidad")
    
    # Definimos las reglas de validación
    validations = [
        {
            "Métrica": "Cobertura (N)",
            "Valor": f"{int(stats['count'])}",
            "Esperado": "> 30 muestras",
            "Estado": "✅ Óptimo" if stats['count'] > 30 else "⚠️ Insuficiente",
            "Justificación": "Necesitamos suficientes datos para que la estadística sea significativa."
        },
        {
            "Métrica": "Varianza (Std Dev)",
            "Valor": f"{stats['std']:.3f}",
            "Esperado": "> 0.100",
            "Estado": "✅ Buena Diferenciación" if stats['std'] > 0.1 else "🔴 Modelo Congelado",
            "Justificación": "Indica si el modelo distingue entre usuarios seguros y vulnerables."
        },
        {
            "Métrica": "Rango Dinámico",
            "Valor": f"{stats['min']:.2f} - {stats['max']:.2f}",
            "Esperado": "0.0 a 1.0",
            "Estado": "✅ Completo" if (stats['max'] - stats['min']) > 0.5 else "⚠️ Rango Corto",
            "Justificación": "El modelo debe ser capaz de detectar tanto casos muy seguros como muy graves."
        },
        {
            "Métrica": "Sesgo (Skewness)",
            "Valor": f"{skewness:.2f}",
            "Esperado": "Entre -1 y 1",
            "Estado": "✅ Equilibrado" if -1 < skewness < 1 else "⚠️ Sesgado",
            "Justificación": "Valores lejanos a 0 indican que el modelo tiende a exagerar hacia un lado."
        }
    ]
    
    # Renderizamos la tabla visualmente
    st.dataframe(
        pd.DataFrame(validations), 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Estado": st.column_config.TextColumn("Diagnóstico")
        }
    )

    # 3. VISUALIZACIÓN AVANZADA (BOX PLOT + HISTOGRAMA)
    # ------------------------------------------------------
    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        st.markdown("##### 📦 Dispersión (Box Plot)")
        st.caption("Muestra la mediana y detecta valores atípicos (puntos fuera de los bigotes).")
        
        # Usamos Altair (nativo en Streamlit) para un BoxPlot profesional
        import altair as alt
        
        chart_box = alt.Chart(df).mark_boxplot(extent='min-max', size=50).encode(
            x=alt.X('probability', title='Probabilidad de Riesgo'),
            color=alt.value("#FF4B4B") # Color rojo corporativo
        ).properties(height=200)
        
        st.altair_chart(chart_box, use_container_width=True)
        
        # Explicación del BoxPlot para directivos
        st.info(f"""
        **Lectura Rápida:**
        El 50% de tus empleados tiene un riesgo entre **{stats['25%']:.0%}** y **{stats['75%']:.0%}**.
        La línea central (**{stats['50%']:.0%}**) es la mediana real de la empresa.
        """)

    with col_viz2:
        st.markdown("##### 📊 Frecuencia (Histograma)")
        st.caption("¿Cómo se agrupan los usuarios?")
        
        # Histograma con Altair para que coincida el estilo
        chart_hist = alt.Chart(df).mark_bar().encode(
            x=alt.X('probability', bin=alt.Bin(maxbins=20), title='Rango de Riesgo'),
            y=alt.Y('count()', title='Cantidad de Usuarios'),
            color=alt.condition(
                alt.datum.probability > 0.7,  # Si es mayor a 0.7
                alt.value('red'),             # Pintar rojo
                alt.value('steelblue')        # Si no, azul
            )
        ).properties(height=200)
        
        st.altair_chart(chart_hist, use_container_width=True)
        
        # Conclusión automática
        if skewness > 1:
            concl = "La mayoría son seguros, pero hay una cola de usuarios muy peligrosos."
        elif skewness < -1:
            concl = "La mayoría son riesgosos, pocos se salvan."
        else:
            concl = "La distribución es normal (Campana de Gauss)."
            
        st.info(f"**Interpretación:** {concl}")

    # 4. VEREDICTO FINAL AUTOMÁTICO
    # ------------------------------------------------------
    # Si pasa las pruebas críticas (Varianza y Rango)
    if stats['std'] > 0.05 and (stats['max'] - stats['min']) > 0.3:
        st.success("🏁 **VEREDICTO:** El modelo es estadísticamente SALUDABLE y apto para toma de decisiones.")
    else:
        st.error("🏁 **VEREDICTO:** El modelo presenta anomalías estadísticas. Revisar datos de entrenamiento.")
        
    st.divider()

    # ==========================================
    # 9. FINAL DE LA PÁGINA
    # ==========================================
    
    # Creamos dos columnas para los botones (Actualizar | Volver)
    col_btn1, col_btn2 = st.columns([1, 4]) # La segunda col es más ancha para separar
    
    with col_btn1:
        if st.button("🔄 Actualizar Datos"):
            run_sql_query.clear()
            st.rerun()
            
    with col_btn2:
        # ⚠️ IMPORTANTE: Pon el nombre EXACTO de tu archivo principal. 
        # Si se llama App.py, déjalo así. Si lo renombras, cámbialo aquí.
        if st.button("⬅️ Volver a la Encuesta"):
            st.switch_page("App.py")

if __name__ == "__main__":
    page_dashboard()