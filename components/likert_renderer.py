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
    Renderiza una página de encuesta estilo Likert moderna y limpia.
    Usa escala numérica 1-5 para mantener la alineación horizontal perfecta.
    """

    # -----------------------------
    # 0. Estilos CSS Personalizados (Para que se vea "Bonito")
    # -----------------------------
    st.markdown("""
        <style>
        /* Estilo de la tarjeta de la pregunta */
        .question-card {
            background-color: #262730; /* Fondo oscuro suave (ajusta si usas modo claro) */
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #41444e;
        }
        .question-text {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 10px;
        }
        /* Ajustar los radio buttons para que estén centrados */
        div.row-widget.stRadio > div {
            justify-content: center;
            gap: 2rem; /* Espacio entre los círculos */
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
    # 1. Inicialización de estado
    # -----------------------------
    if "responses" not in st.session_state:
        st.session_state.responses = {}
    if "page" not in st.session_state:
        st.session_state.page = 1

    # -----------------------------
    # 2. Header y Leyenda
    # -----------------------------
    st.title(title)
    st.write(description)
    
    # LEYENDA VISUAL: Explica la escala una sola vez arriba
    st.markdown("""
    <div class="legend-box">
        <b>Escala de Respuesta:</b><br>
        1 = Muy en Desacuerdo &nbsp;|&nbsp; 
        2 = En Desacuerdo &nbsp;|&nbsp; 
        3 = Neutro &nbsp;|&nbsp; 
        4 = De Acuerdo &nbsp;|&nbsp; 
        5 = Muy de Acuerdo
    </div>
    """, unsafe_allow_html=True)

    unanswered = []
    
    # Opciones numéricas limpias (garantizan una sola fila)
    options_numeric = [1, 2, 3, 4, 5]
    
    # Mapeo inverso para guardar el valor correcto en tu lógica
    # Asumimos que LIKERT_5 tiene las claves como texto y valores como números, 
    # o si LIKERT_5 ya mapea Texto -> Numero, usamos los números directamente.
    
    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    
    for i, q in enumerate(questions):
        # Contenedor visual (Tarjeta)
        with st.container():
            st.markdown(f"""
            <div class="question-card">
                <div class="question-text">{i+1}. {q['text']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Recuperar respuesta previa
            saved_val = st.session_state.responses.get(q["code"])
            
            # Lógica de inversión si la pregunta es reversa
            display_val = saved_val
            if saved_val is not None and q.get("reverse", False):
                display_val = invert_likert(saved_val)

            # Radio Button Numérico (Horizontal y limpio)
            # Usamos label_visibility="collapsed" para que no repita el texto
            selection = st.radio(
                label=q['text'], 
                options=options_numeric,
                index=options_numeric.index(display_val) if display_val in options_numeric else None,
                horizontal=True,
                label_visibility="collapsed",
                key=f"{q['code']}_ui",
                help="1: Muy en desacuerdo ... 5: Muy de acuerdo"
            )

            # Guardado de respuesta
            if selection is None:
                unanswered.append(q["code"])
            else:
                # Calculamos el valor real a guardar
                final_value = selection
                if q.get("reverse", False):
                    final_value = invert_likert(selection)
                
                st.session_state.responses[q["code"]] = final_value

    st.divider()

    # -----------------------------
    # 4. Navegación
    # -----------------------------
    col1, col2, col3 = st.columns([1, 3, 1])

    if prev_page is not None:
        with col1:
            st.button("⬅️ Atrás", on_click=lambda: st.session_state.update(page=prev_page), use_container_width=True)

    with col3:
        # El botón se deshabilita si faltan respuestas
        btn_disabled = len(unanswered) > 0
        btn_text = f"Faltan {len(unanswered)}" if btn_disabled else "Siguiente ➡️"
        
        st.button(
            btn_text,
            disabled=btn_disabled,
            on_click=lambda: st.session_state.update(page=next_page),
            type="primary" if not btn_disabled else "secondary",
            use_container_width=True
        )