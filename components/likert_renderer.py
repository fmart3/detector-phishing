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
    Renderiza encuesta usando st.selectbox centrado y estilizado.
    """

    # -----------------------------
    # 0. CSS PARA SELECTBOX CENTRADO
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
            margin-bottom: 15px; 
            text-align: center; /* Centramos también la pregunta para simetría */
        }

        /* 2. ESTILOS DEL SELECTBOX */
        
        /* Centrar el texto DENTRO de la caja de selección cerrada */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            text-align: center;
            justify-content: center;
            font-weight: 500;
            font-size: 16px;
        }

        /* Centrar las opciones cuando se despliega la lista */
        div[role="listbox"] li {
            text-align: center;
            justify-content: center;
        }
        
        /* Ajuste para que ocupe el ancho visualmente agradable */
        div[data-testid="stSelectbox"] {
            width: 100%;
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

    # Definimos el diccionario de etiquetas para que el selectbox sea descriptivo
    # Esto ayuda al usuario a no tener que mirar una leyenda externa
    likert_labels = {
        1: "1 - Muy en desacuerdo",
        2: "2 - En desacuerdo",
        3: "3 - Neutro",
        4: "4 - De acuerdo",
        5: "5 - Muy de acuerdo"
    }
    options_numeric = [1, 2, 3, 4, 5]

    # -----------------------------
    # 2. Header
    # -----------------------------
    st.title(title)
    st.write(description)
    st.markdown("---")

    unanswered = []

    # -----------------------------
    # 3. Renderizado de Preguntas
    # -----------------------------
    for i, q in enumerate(questions):
        # Usamos container para agrupar visualmente
        with st.container():
            # Abrimos la tarjeta visual
            st.markdown(f"""
            <div class="question-card">
                <div class="question-text">{i+1}. {q['text']}</div>
            """, unsafe_allow_html=True)
            
            # --- LÓGICA DE VALORES ---
            saved_raw = st.session_state.responses.get(q["code"])
            
            # Si hay valor guardado, calculamos cuál mostrar (considerando reverso)
            display_val = None
            if saved_raw is not None:
                if q.get("reverse", False):
                    display_val = invert_likert(saved_raw)
                else:
                    display_val = saved_raw

            # Calculamos el índice para el selectbox
            # Si display_val es 3, el index es 2 (porque la lista empieza en 0)
            idx = options_numeric.index(display_val) if display_val in options_numeric else None

            # --- WIDGET SELECTBOX ---
            selection = st.selectbox(
                label=f"Respuesta a la pregunta {i+1}", # Label oculto por accesibilidad
                options=options_numeric,
                format_func=lambda x: likert_labels[x], # Muestra texto bonito
                index=idx,
                placeholder="Seleccione una opción...", # Texto cuando está vacío
                label_visibility="collapsed",
                key=f"{q['code']}_select"
            )
            
            # Cerramos el div de la tarjeta
            st.markdown("</div>", unsafe_allow_html=True)

            # --- GUARDADO ---
            if selection is None:
                unanswered.append(q["code"])
            else:
                final_value = selection
                # Aplicamos lógica inversa si es necesario ANTES de guardar
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
        btn_disabled = len(unanswered) > 0
        
        if btn_disabled:
            btn_text = f"Faltan {len(unanswered)}"
            help_text = "Por favor responde todas las preguntas para continuar."
        else:
            btn_text = "Siguiente ➡️"
            help_text = None

        st.button(
            btn_text,
            disabled=btn_disabled,
            on_click=lambda: st.session_state.update(page=next_page),
            type="primary" if not btn_disabled else "secondary",
            use_container_width=True,
            help=help_text
        )