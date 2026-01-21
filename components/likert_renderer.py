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
    Renderiza encuesta con distribución horizontal completa (Justified).
    """

    # -----------------------------
    # 0. CSS MEJORADO (Distribución Ancha)
    # -----------------------------
    st.markdown("""
        <style>
        /* 1. Tarjeta de la pregunta */
        .question-card {
            background-color: #262730; 
            padding: 25px; /* Un poco más de padding */
            border-radius: 12px;
            margin-bottom: 20px;
            border: 1px solid #41444e;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .question-text {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 15px; /* Más espacio entre texto y botones */
        }

        /* 2. MAGIA DE DISTRIBUCIÓN HORIZONTAL */
        /* Esto afecta al contenedor de los circulitos */
        div.row-widget.stRadio > div[role="radiogroup"] {
            justify-content: space-between; /* Distribuye de extremo a extremo */
            width: 100%;       /* Ocupa todo el ancho disponible */
            padding: 0 20px;   /* Un pequeño margen interno para que no toquen el borde exacto */
        }

        /* 3. Hacer los números/opciones más grandes y clicables */
        div.row-widget.stRadio label div[data-testid="stMarkdownContainer"] p {
            font-size: 18px !important; /* Números más grandes */
            font-weight: bold;
        }

        /* Leyenda superior */
        .legend-box {
            background-color: #0e1117;
            border: 1px solid #41444e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            text-align: center;
            font-size: 14px;
            color: #fafafa;
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
    
    st.markdown("""
    <div class="legend-box">
        <b>Escala:</b> &nbsp; 
        1 (Muy en Desacuerdo) &nbsp; ↔ &nbsp; 
        5 (Muy de Acuerdo)
    </div>
    """, unsafe_allow_html=True)

    unanswered = []
    options_numeric = [1, 2, 3, 4, 5]
    
    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        with st.container():
            # Abrimos la tarjeta visual
            st.markdown(f"""
            <div class="question-card">
                <div class="question-text">{i+1}. {q['text']}</div>
            """, unsafe_allow_html=True) # Nota: No cerramos el div aquí para envolver el radio (truco visual) o cerramos y el radio queda dentro visualmente por el fondo.
            
            # Corrección: El st.radio no se puede meter DENTRO del div HTML de arriba fácilmente.
            # Mejor estrategia: Cerramos el div del texto, pero visualmente parecerá parte de lo mismo si el fondo es igual.
            # Pero para que quede PERFECTO, el st.radio queda fuera del HTML puro. 
            # El CSS global de arriba ajustará el st.radio.
            
            st.markdown("</div>", unsafe_allow_html=True) 

            # Lógica de valor
            saved_val = st.session_state.responses.get(q["code"])
            display_val = saved_val
            if saved_val is not None and q.get("reverse", False):
                display_val = invert_likert(saved_val)

            # RADIO BUTTON
            selection = st.radio(
                label=q['text'], # Hidden by label_visibility
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
            
            # Espaciador sutil
            st.write("") 

    st.divider()

    # -----------------------------
    # 4. Botones
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