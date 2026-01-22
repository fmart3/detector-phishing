import streamlit as st
from utils.scales import LIKERT_5, invert_likert

def render_likert_page(
    title: str,
    description: str,
    questions: list,
    next_page: int,
    prev_page: int | None = None
):
    """
    Renderiza encuesta con distribución horizontal TOTAL (Full Justified).
    Usa 'flex: 1' para obligar a cada opción a ocupar el 20% del ancho.
    """

    # -----------------------------
    # 0. CSS AGRESIVO (Distribución Forzada)
    # -----------------------------
    st.markdown("""
        <style>
        /* 1. Tarjeta de la pregunta */
        .question-card {
            background-color: #262730; 
            padding: 20px 25px; 
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid #41444e;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .question-text {
            font-size: 19px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 15px;
        }

        /* 2. FORZAR ANCHO TOTAL EN LOS RADIO BUTTONS */
        
        /* Contenedor principal del widget */
        div.row-widget.stRadio {
            width: 100% !important;
            padding-bottom: 5px;
        }

        /* El grupo flex que contiene los botones */
        div.row-widget.stRadio > div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            gap: 0 !important; /* Eliminamos gaps nativos para manejarlo nosotros */
        }

        /* CADA OPCIÓN INDIVIDUAL (El item 1, 2, 3...) */
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            flex: 1 !important; /* CLAVE: Cada opción crece para ocupar espacio igual */
            display: flex !important;
            flex-direction: column-reverse; /* Pone el número ARRIBA del círculo si quieres, o normal */
            align-items: center !important; /* Centra el círculo en su 20% de espacio */
            justify-content: center !important;
            margin-right: 0px !important; /* Elimina margen derecho de Streamlit */
            background-color: transparent !important;
            cursor: pointer;
        }

        /* 3. Estilo del Texto (Los números 1, 2, 3...) */
        div.row-widget.stRadio label div[data-testid="stMarkdownContainer"] p {
            font-size: 20px !important; 
            font-weight: bold;
            margin-bottom: 5px !important; /* Separación entre número y círculo */
            text-align: center;
        }

        /* 4. Leyenda superior */
        .legend-box {
            background-color: #0e1117;
            border: 1px solid #41444e;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-size: 14px;
            color: #bdc2c9;
        }
        
        .legend-scale {
            display: flex;
            justify-content: space-between; /* Extremo a extremo */
            margin-top: 5px;
            font-weight: bold;
            color: #ffffff;
            padding: 0 25px; /* Un poco de padding para alinearse visualmente con los centros */
        }
        </style>
    """, unsafe_allow_html=True)

    # -----------------------------
    # 1. Inicialización
    # -----------------------------
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "page" not in st.session_state:
        st.session_state.page = 1

    # -----------------------------
    # 2. Header
    # -----------------------------
    st.title(title)
    st.write(description)
    
    # Leyenda alineada visualmente
    st.markdown("""
    <div class="legend-box">
        <div style="text-align:center; margin-bottom:5px">Selecciona el grado de acuerdo:</div>
        <div class="legend-scale">
            <span style="text-align:left">1<br><small style="font-weight:normal; color:#aaa">Muy en<br>desacuerdo</small></span>
            <span style="text-align:right">5<br><small style="font-weight:normal; color:#aaa">Muy de<br>acuerdo</small></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    unanswered = []
    options_numeric = [1, 2, 3, 4, 5]
    
    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        # Contenedor visual
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <div class="question-text">{i+1}. {q['text']}</div>
            """, unsafe_allow_html=True) 
            
            # Cerramos el div del texto antes del radio
            st.markdown("</div>", unsafe_allow_html=True) 

            # Lógica de valor
            saved_val = st.session_state.responses.get(q["code"])
            display_val = saved_val
            if saved_val is not None and q.get("reverse", False):
                display_val = invert_likert(saved_val)

            # RADIO BUTTON
            selection = st.radio(
                label=q['text'], 
                options=options_numeric,
                index=options_numeric.index(display_val) if display_val in options_numeric else None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"{q['code']}_ui"
            )

            if selection is None:
                unanswered.append(q["code"])
            else:
                final_value = selection
                if q.get("reverse", False):
                    final_value = invert_likert(selection)
                st.session_state.responses[q["code"]] = final_value
            
            # Espaciador visual pequeño
            st.markdown("<div style='margin-bottom: 5px'></div>", unsafe_allow_html=True)

    st.divider()

    # -----------------------------
    # 4. Navegación
    # -----------------------------
    col1, col2, col3 = st.columns([1, 3, 1])

    if prev_page is not None:
        with col1:
            st.button("⬅️ Atrás", on_click=lambda: st.session_state.update(page=prev_page), use_container_width=True)

    with col3:
        btn_disabled = len(unanswered) > 0
        btn_text = f"Faltan {len(unanswered)}" if btn_disabled else "Siguiente ➡️"
        
        st.button(
            btn_text,
            disabled=btn_disabled,
            on_click=lambda: st.session_state.update(page=next_page),
            type="primary" if not btn_disabled else "secondary",
            use_container_width=True
        )