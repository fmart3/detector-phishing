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
    Renderiza encuesta con distribución horizontal PERFECTA usando CSS Grid estricto.
    """

    # -----------------------------
    # 0. CSS GRID ESTRICTO (Clean Layout)
    # -----------------------------
    st.markdown("""
        <style>
        /* 1. Tarjeta de la pregunta (Contenedor Gris) */
        .question-card {
            background-color: #262730; 
            padding: 20px 30px; 
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid #41444e;
        }
        
        .question-text {
            font-size: 19px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 25px; /* Espacio antes de los círculos */
        }

        /* 2. FORZAR LA ESTRUCTURA DEL RADIO BUTTON */
        
        /* ================================
        STREAMLIT RADIO – BASEWEB FIX
        ================================ */

        /* Contenedor total */
        div.stRadio {
            width: 100% !important;
        }

        /* BaseWeb radio group */
        div.stRadio [data-baseweb="radio"] {
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            width: 100% !important;
            justify-items: center !important;
        }

        /* Cada opción */
        div.stRadio [data-baseweb="radio"] > label {
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Número (1–5) */
        div.stRadio label span {
            font-size: 20px !important;
            font-weight: 600 !important;
            margin-bottom: 6px !important;
        }

        /* El círculo */
        div.stRadio input[type="radio"] {
            margin: 0 auto !important;
        }

        /* 3. Leyenda superior explicativa */
        .legend-box {
            background-color: #0e1117;
            border: 1px solid #41444e;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .legend-scale {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr 1fr; /* Misma grilla que los botones */
            text-align: center;
            font-size: 13px;
            color: #bdc2c9;
            margin-top: 5px;
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
    # 2. Header & Leyenda
    # -----------------------------
    st.title(title)
    st.write(description)
    
    # Leyenda alineada EXACTAMENTE igual que los botones (usando grid también)
    st.markdown("""
    <div class="legend-box">
        <div style="text-align:center; font-weight:bold; margin-bottom:10px; color:white;">Guía de Respuesta</div>
        <div class="legend-scale">
            <div style="text-align: center">1<br>Muy en<br>desacuerdo</div>
            <div></div> <div style="text-align: center">3<br>Neutro</div>
            <div></div> <div style="text-align: center">5<br>Muy de<br>acuerdo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    unanswered = []
    options_numeric = [1, 2, 3, 4, 5]
    
    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        with st.container():
            # Encabezado de la tarjeta
            st.markdown('<div class="question-card">', unsafe_allow_html=True)
            
            st.write("DEBUG:", q["code"], i)

            st.radio(
                label="",
                options=options_numeric,
                horizontal=True,
                key=f"{q['code']}_ui"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Recuperar valor previo
            saved_val = st.session_state.responses.get(q["code"])
            display_val = saved_val
            if saved_val is not None and q.get("reverse", False):
                display_val = invert_likert(saved_val)

            # WIDGET
            selection = st.radio(
                label="", 
                options=options_numeric,
                index=options_numeric.index(display_val) if display_val in options_numeric else None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"{q['code']}_ui"
            )

            # Guardar respuesta
            if selection is None:
                unanswered.append(q["code"])
            else:
                final_value = selection
                if q.get("reverse", False):
                    final_value = invert_likert(selection)
                st.session_state.responses[q["code"]] = final_value
            
            # Espacio visual inferior
            st.write("")

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